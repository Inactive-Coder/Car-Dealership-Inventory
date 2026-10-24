import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import httpx
import pytest

from app.core.database import get_db
from app.core.security import create_access_token
from app.main import app
from app.models.user import User
from app.models.vehicle import Vehicle


class Rows:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class Result:
    def __init__(self, row):
        self.row = row

    def scalar_one_or_none(self):
        return self.row


class FakeSession:
    def __init__(self, scalar_results=None, rows=None, execute_result=None):
        self.scalar_results = list(scalar_results or [])
        self.rows = list(rows or [])
        self.execute_result = execute_result
        self.executed_statement = None
        self.scalar_statements = []
        self.list_statement = None
        self.committed = False

    def scalar(self, statement):
        self.scalar_statements.append(statement)
        return self.scalar_results.pop(0) if self.scalar_results else None

    def scalars(self, statement):
        self.list_statement = statement
        return Rows(self.rows)

    def execute(self, statement):
        self.executed_statement = statement
        return Result(self.execute_result)

    def commit(self):
        self.committed = True

    def add(self, row):
        self.added = row

    def refresh(self, row):
        if row.id is None:
            row.id = uuid4()
        now = datetime.now(timezone.utc)
        if row.created_at is None:
            row.created_at = now
        if row.updated_at is None:
            row.updated_at = now

    def delete(self, row):
        self.deleted = row

    def close(self):
        pass


def user(role="user"):
    return User(
        id=uuid4(), email="driver@example.com", password_hash="hash", role=role,
        created_at=datetime.now(timezone.utc),
    )


def vehicle(quantity=0):
    now = datetime.now(timezone.utc)
    return Vehicle(
        id=uuid4(), make="Volvo", model="XC60", category="SUV", price=Decimal("25000.00"),
        quantity=quantity, created_at=now, updated_at=now,
    )


def bearer_token(account):
    return create_access_token(str(account.id), account.role)[0]


def test_inventory_endpoint_requires_authentication():
    async def request_inventory():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get("/api/vehicles")

    response = asyncio.run(request_inventory())
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


@pytest.mark.parametrize("token", ["not-a-jwt", "eyJhbGciOiJub25lIn0.eyJzdWIiOiJ4In0."])
def test_inventory_rejects_invalid_tokens(token):
    async def request_inventory():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get("/api/vehicles", headers={"Authorization": f"Bearer {token}"})

    response = asyncio.run(request_inventory())
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_authenticated_inventory_includes_zero_stock_vehicles():
    account = user()
    out_of_stock = vehicle(quantity=0)
    session = FakeSession(scalar_results=[account, 1], rows=[out_of_stock])
    app.dependency_overrides[get_db] = lambda: session

    async def request_inventory():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get("/api/vehicles", headers={"Authorization": f"Bearer {bearer_token(account)}"})

    try:
        response = asyncio.run(request_inventory())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["quantity"] == 0


def test_regular_user_cannot_create_vehicle():
    account = user(role="user")
    session = FakeSession(scalar_results=[account])
    app.dependency_overrides[get_db] = lambda: session

    async def request_create():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.post(
                "/api/vehicles",
                headers={"Authorization": f"Bearer {bearer_token(account)}"},
                json={"make": "Volvo", "model": "XC60", "category": "SUV", "price": "25000.00", "quantity": 2},
            )

    try:
        response = asyncio.run(request_create())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert not session.committed


def test_purchase_uses_conditional_atomic_decrement():
    from app.services.vehicles import purchase_one
    from sqlalchemy.dialects import postgresql

    available = vehicle(quantity=3)
    session = FakeSession(execute_result=available)
    result = purchase_one(available.id, session)
    sql = str(session.executed_statement.compile(dialect=postgresql.dialect()))

    assert result is available
    assert "quantity >" in sql
    assert "RETURNING" in sql
    assert session.committed


def test_out_of_stock_purchase_fails_without_commit():
    import pytest
    from app.services.vehicles import OutOfStockError, purchase_one
    from sqlalchemy.dialects import postgresql

    existing = vehicle(quantity=0)
    session = FakeSession(scalar_results=[existing.id])
    with pytest.raises(OutOfStockError):
        purchase_one(existing.id, session)
    sql = str(session.executed_statement.compile(dialect=postgresql.dialect()))

    assert "quantity >" in sql
    assert not session.committed


def test_search_combines_case_insensitive_text_and_inclusive_price_filters():
    from sqlalchemy.dialects import postgresql

    account = user()
    session = FakeSession(scalar_results=[account, 0])
    app.dependency_overrides[get_db] = lambda: session

    async def request_search():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get(
                "/api/vehicles/search?make=vol&model=xc&category=suv&min_price=25000&max_price=30000",
                headers={"Authorization": f"Bearer {bearer_token(account)}"},
            )

    try:
        response = asyncio.run(request_search())
    finally:
        app.dependency_overrides.clear()

    sql = str(session.list_statement.compile(dialect=postgresql.dialect()))
    assert response.status_code == 200
    assert "ILIKE" in sql
    assert "lower(vehicles.category)" in sql
    assert "vehicles.price >=" in sql
    assert "vehicles.price <=" in sql


def test_admin_can_create_vehicle():
    account = user(role="admin")
    session = FakeSession(scalar_results=[account])
    app.dependency_overrides[get_db] = lambda: session

    async def request_create():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.post(
                "/api/vehicles",
                headers={"Authorization": f"Bearer {bearer_token(account)}"},
                json={"make": "Volvo", "model": "XC60", "category": "SUV", "price": "25000.00", "quantity": 2},
            )

    try:
        response = asyncio.run(request_create())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["quantity"] == 2
    assert session.committed


def test_restock_requires_positive_integer():
    account = user(role="admin")
    session = FakeSession(scalar_results=[account])
    app.dependency_overrides[get_db] = lambda: session

    async def request_restock():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.post(
                f"/api/vehicles/{uuid4()}/restock",
                headers={"Authorization": f"Bearer {bearer_token(account)}"},
                json={"quantity": 0},
            )

    try:
        response = asyncio.run(request_restock())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert not session.committed


def test_restock_uses_atomic_quantity_increment():
    from app.services.vehicles import restock_vehicle
    from sqlalchemy.dialects import postgresql

    updated = vehicle(quantity=8)
    session = FakeSession(execute_result=updated)
    result = restock_vehicle(updated.id, 5, session)
    sql = str(session.executed_statement.compile(dialect=postgresql.dialect()))

    assert result is updated
    assert "vehicles.quantity +" in sql
    assert "RETURNING" in sql
    assert session.committed


def test_update_missing_vehicle_returns_not_found():
    account = user(role="admin")
    session = FakeSession(scalar_results=[account, None])
    app.dependency_overrides[get_db] = lambda: session

    async def request_update():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.put(
                f"/api/vehicles/{uuid4()}",
                headers={"Authorization": f"Bearer {bearer_token(account)}"},
                json={"make": "Volvo", "model": "XC60", "category": "SUV", "price": "25000.00", "quantity": 2},
            )

    try:
        response = asyncio.run(request_update())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert not session.committed


def test_expired_token_is_rejected():
    import jwt
    from datetime import timedelta
    from app.core.config import get_settings

    settings = get_settings()
    past = datetime.now(timezone.utc) - timedelta(minutes=5)
    token = jwt.encode(
        {"sub": str(uuid4()), "role": "user", "iat": past, "exp": past + timedelta(minutes=1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    async def request_inventory():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get("/api/vehicles", headers={"Authorization": f"Bearer {token}"})

    response = asyncio.run(request_inventory())
    assert response.status_code == 401


def test_search_rejects_minimum_above_maximum():
    account = user()
    session = FakeSession(scalar_results=[account])
    app.dependency_overrides[get_db] = lambda: session

    async def request_search():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get(
                "/api/vehicles/search?min_price=30000&max_price=25000",
                headers={"Authorization": f"Bearer {bearer_token(account)}"},
            )

    try:
        response = asyncio.run(request_search())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_admin_can_update_vehicle():
    account = user(role="admin")
    existing = vehicle(quantity=3)
    session = FakeSession(scalar_results=[account, existing])
    app.dependency_overrides[get_db] = lambda: session

    async def request_update():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.put(
                f"/api/vehicles/{existing.id}",
                headers={"Authorization": f"Bearer {bearer_token(account)}"},
                json={"make": "Volvo", "model": "XC90", "category": "SUV", "price": "30000.00", "quantity": 5},
            )

    try:
        response = asyncio.run(request_update())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["model"] == "XC90"
    assert response.json()["quantity"] == 5
    assert session.committed


def test_admin_can_delete_vehicle():
    account = user(role="admin")
    existing = vehicle(quantity=0)
    session = FakeSession(scalar_results=[account, existing])
    app.dependency_overrides[get_db] = lambda: session

    async def request_delete():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.delete(
                f"/api/vehicles/{existing.id}",
                headers={"Authorization": f"Bearer {bearer_token(account)}"},
            )

    try:
        response = asyncio.run(request_delete())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 204
    assert session.deleted is existing
    assert session.committed


def test_missing_vehicle_purchase_returns_not_found_without_commit():
    from app.services.vehicles import VehicleNotFoundError, purchase_one

    session = FakeSession()
    with pytest.raises(VehicleNotFoundError):
        purchase_one(uuid4(), session)
    assert not session.committed
