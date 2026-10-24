import asyncio
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import delete, select

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.main import app
from app.models.user import User
from app.models.vehicle import Vehicle


def override_database(factory):
    def get_test_db():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    return get_test_db


@pytest.mark.integration
def test_registration_persists_hash_and_login_authenticates(postgres_test_session_factory):
    sessions = postgres_test_session_factory
    email = f"driver-{uuid4()}@example.com"
    password = "integration-driver-password"
    app.dependency_overrides[get_db] = override_database(sessions)

    async def run_workflow():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            registered = await client.post("/api/auth/register", json={"email": email, "password": password})
            duplicate = await client.post("/api/auth/register", json={"email": email, "password": password})
            login = await client.post("/api/auth/login", json={"email": email.upper(), "password": password})
            return registered, duplicate, login

    try:
        registered, duplicate, login = asyncio.run(run_workflow())
        assert registered.status_code == 201
        assert registered.json()["role"] == "user"
        assert "password_hash" not in registered.json()
        assert duplicate.status_code == 409
        assert login.status_code == 200
        assert login.json()["user"]["email"] == email
        assert login.json()["access_token"]

        with sessions() as session:
            account = session.scalar(select(User).where(User.email == email))
            assert account is not None
            assert account.role == "user"
            assert verify_password(password, account.password_hash)
    finally:
        app.dependency_overrides.clear()
        with sessions() as session:
            account = session.scalar(select(User).where(User.email == email))
            if account is not None:
                session.delete(account)
                session.commit()


@pytest.mark.integration
def test_admin_vehicle_lifecycle_search_purchase_restock_and_delete(postgres_test_session_factory):
    sessions = postgres_test_session_factory
    suffix = uuid4().hex
    admin = User(email=f"admin-{suffix}@example.com", password_hash=hash_password("integration-admin-password"), role="admin")
    customer = User(email=f"customer-{suffix}@example.com", password_hash=hash_password("integration-customer-password"), role="user")
    with sessions() as session:
        session.add_all([admin, customer])
        session.commit()
        session.refresh(admin)
        session.refresh(customer)

    admin_token, _ = create_access_token(str(admin.id), admin.role)
    customer_token, _ = create_access_token(str(customer.id), customer.role)
    app.dependency_overrides[get_db] = override_database(sessions)
    vehicle_id = None

    async def run_workflow():
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
        headers_customer = {"Authorization": f"Bearer {customer_token}"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            forbidden_create = await client.post(
                "/api/vehicles",
                headers=headers_customer,
                json={"make": "Volvo", "model": f"XC-{suffix}", "category": "SUV", "price": "42000.00", "quantity": 1},
            )
            created = await client.post(
                "/api/vehicles",
                headers=headers_admin,
                json={"make": "Volvo", "model": f"XC-{suffix}", "category": "SUV", "price": "42000.00", "quantity": 1},
            )
            found = await client.get(
                f"/api/vehicles/search?make=vol&model={suffix[:8]}&category=suv&min_price=42000&max_price=42000",
                headers=headers_customer,
            )
            updated = await client.put(
                f"/api/vehicles/{created.json()['id']}",
                headers=headers_admin,
                json={"make": "Volvo", "model": f"XC-{suffix}", "category": "SUV", "price": "42000.00", "quantity": 1},
            )
            purchased = await client.post(f"/api/vehicles/{created.json()['id']}/purchase", headers=headers_customer)
            exhausted = await client.post(f"/api/vehicles/{created.json()['id']}/purchase", headers=headers_customer)
            restocked = await client.post(
                f"/api/vehicles/{created.json()['id']}/restock",
                headers=headers_admin,
                json={"quantity": 3},
            )
            deleted = await client.delete(f"/api/vehicles/{created.json()['id']}", headers=headers_admin)
            return forbidden_create, created, found, updated, purchased, exhausted, restocked, deleted

    try:
        responses = asyncio.run(run_workflow())
        forbidden_create, created, found, updated, purchased, exhausted, restocked, deleted = responses
        assert forbidden_create.status_code == 403
        assert created.status_code == 201
        vehicle_id = created.json()["id"]
        assert found.status_code == 200
        assert any(item["id"] == vehicle_id for item in found.json()["items"])
        assert updated.status_code == 200
        assert purchased.status_code == 200 and purchased.json()["quantity"] == 0
        assert exhausted.status_code == 409
        assert exhausted.json()["error"]["code"] == "out_of_stock"
        assert restocked.status_code == 200 and restocked.json()["quantity"] == 3
        assert deleted.status_code == 204
        with sessions() as session:
            assert session.get(Vehicle, UUID(vehicle_id)) is None
    finally:
        app.dependency_overrides.clear()
        with sessions() as session:
            if vehicle_id is not None:
                session.execute(delete(Vehicle).where(Vehicle.id == UUID(vehicle_id)))
            session.execute(delete(User).where(User.id.in_([admin.id, customer.id])))
            session.commit()
