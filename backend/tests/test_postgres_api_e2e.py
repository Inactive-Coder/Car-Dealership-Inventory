import asyncio
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import delete, select

from app.core.dependencies import get_db
from app.main import app
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.user import RegisterRequest
from app.services.auth import provision_initial_admin


def override_database(factory):
    def get_test_db():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    return get_test_db


@pytest.mark.integration
def test_postgres_user_and_admin_workflows_through_api(postgres_test_session_factory):
    """Exercise auth, filters, demo-confirmed purchase, stock, and admin CRUD on PostgreSQL."""
    sessions = postgres_test_session_factory
    suffix = uuid4().hex
    admin_email = f"api-admin-{suffix}@example.com"
    buyer_email = f"api-buyer-{suffix}@example.com"
    admin_password = f"postgres-admin-{suffix}-A9!"
    buyer_password = f"postgres-buyer-{suffix}-B8!"
    initial_model = f"City-{suffix[:8]}"
    updated_model = f"Accord-{suffix[:8]}"
    vehicle_id: UUID | None = None

    with sessions() as session:
        existing_admin = session.scalar(select(User.id).where(User.role == "admin").limit(1))
        assert existing_admin is None, "TEST_DATABASE_URL must be reserved for isolated integration tests"
        provision_initial_admin(
            RegisterRequest(email=admin_email, password=admin_password),
            session,
        )

    app.dependency_overrides[get_db] = override_database(sessions)

    async def exercise_api():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            registered = await client.post(
                "/api/auth/register",
                json={"email": buyer_email, "password": buyer_password},
            )
            assert registered.status_code == 201
            assert registered.json()["role"] == "user"

            buyer_login = await client.post(
                "/api/auth/login",
                json={"email": buyer_email, "password": buyer_password},
            )
            admin_login = await client.post(
                "/api/auth/login",
                json={"email": admin_email, "password": admin_password},
            )
            assert buyer_login.status_code == 200
            assert admin_login.status_code == 200
            buyer_headers = {"Authorization": f"Bearer {buyer_login.json()['access_token']}"}
            admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

            vehicle_data = {
                "make": "E2E Honda",
                "model": initial_model,
                "category": "Sedan",
                "price": "1234567.00",
                "quantity": 1,
            }
            denied = await client.post("/api/vehicles", headers=buyer_headers, json=vehicle_data)
            assert denied.status_code == 403

            created = await client.post("/api/vehicles", headers=admin_headers, json=vehicle_data)
            assert created.status_code == 201
            created_vehicle = created.json()
            created_id = UUID(created_vehicle["id"])
            assert created_vehicle["quantity"] == 1

            searched = await client.get(
                "/api/vehicles/search",
                headers=buyer_headers,
                params={
                    "make": "honda",
                    "model": suffix[:8],
                    "category": "sedan",
                    "min_price": "1234567.00",
                    "max_price": "1234567.00",
                },
            )
            assert searched.status_code == 200
            assert [item["id"] for item in searched.json()["items"]] == [str(created_id)]

            # Cancel is client-side: with no purchase request, the persisted stock remains unchanged.
            before_cancel = await client.get("/api/vehicles", headers=buyer_headers)
            assert next(item for item in before_cancel.json()["items"] if item["id"] == str(created_id))["quantity"] == 1
            after_cancel = await client.get("/api/vehicles", headers=buyer_headers)
            assert next(item for item in after_cancel.json()["items"] if item["id"] == str(created_id))["quantity"] == 1

            confirmed = await client.post(f"/api/vehicles/{created_id}/purchase", headers=buyer_headers)
            assert confirmed.status_code == 200
            assert confirmed.json()["quantity"] == 0
            exhausted = await client.post(f"/api/vehicles/{created_id}/purchase", headers=buyer_headers)
            assert exhausted.status_code == 409
            assert exhausted.json()["error"]["code"] == "out_of_stock"

            restocked = await client.post(
                f"/api/vehicles/{created_id}/restock",
                headers=admin_headers,
                json={"quantity": 3},
            )
            assert restocked.status_code == 200
            assert restocked.json()["quantity"] == 3

            updated_data = {**vehicle_data, "model": updated_model, "quantity": 3}
            updated = await client.put(
                f"/api/vehicles/{created_id}",
                headers=admin_headers,
                json=updated_data,
            )
            assert updated.status_code == 200
            assert updated.json()["model"] == updated_data["model"]

            deleted = await client.delete(f"/api/vehicles/{created_id}", headers=admin_headers)
            assert deleted.status_code == 204
            return created_id

    try:
        vehicle_id = asyncio.run(exercise_api())
    finally:
        app.dependency_overrides.clear()
        with sessions() as session:
            if vehicle_id is not None:
                session.execute(delete(Vehicle).where(Vehicle.id == vehicle_id))
            session.execute(
                delete(Vehicle).where(
                    Vehicle.make == "E2E Honda",
                    Vehicle.model.in_([initial_model, updated_model]),
                )
            )
            session.execute(delete(User).where(User.email.in_([admin_email, buyer_email])))
            session.commit()
