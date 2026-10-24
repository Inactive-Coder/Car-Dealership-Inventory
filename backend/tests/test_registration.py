import asyncio
from datetime import datetime, timezone
from uuid import UUID

import httpx

from app.main import app
from app.core.database import get_db
from app.core.security import verify_password


class FakeSession:
    """Keeps this focused route test independent of a running database."""

    def __init__(self):
        self.user = None
        self.lookup_result = None

    def scalar(self, _statement):
        return self.lookup_result

    def add(self, user):
        self.user = user

    def commit(self):
        pass

    def refresh(self, user):
        user.id = UUID("f4f7f507-625b-4f6b-a4fa-6a1f51986a59")
        user.created_at = datetime.now(timezone.utc)

    def rollback(self):
        pass

    def close(self):
        pass


def test_registration_creates_regular_user_with_hashed_password():
    """Registration returns safe user data and hashes passwords."""
    session = FakeSession()
    app.dependency_overrides[get_db] = lambda: session

    async def request_registration():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/api/auth/register",
                json={"email": "driver@example.com", "password": "a-long-test-password"},
            )

    try:
        response = asyncio.run(request_registration())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == "driver@example.com"
    assert payload["role"] == "user"
    assert UUID(payload["id"])
    assert "password" not in payload
    assert "password_hash" not in payload
    assert session.user.email == "driver@example.com"
    assert session.user.role == "user"
    assert verify_password("a-long-test-password", session.user.password_hash)


def test_login_returns_signed_access_token_for_valid_credentials():
    from app.models.user import User
    from app.core.security import hash_password
    from datetime import datetime, timezone
    from uuid import uuid4

    session = FakeSession()
    session.lookup_result = User(
        id=uuid4(),
        email="driver@example.com",
        password_hash=hash_password("a-long-test-password"),
        role="user",
        created_at=datetime.now(timezone.utc),
    )
    app.dependency_overrides[get_db] = lambda: session

    async def request_login():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/api/auth/login",
                json={"email": "driver@example.com", "password": "a-long-test-password"},
            )

    try:
        response = asyncio.run(request_login())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["expires_in"] > 0
    assert payload["user"]["email"] == "driver@example.com"
    assert payload["access_token"]


def test_duplicate_registration_returns_conflict_without_storing_another_user():
    from app.models.user import User

    session = FakeSession()
    session.lookup_result = User(email="driver@example.com", password_hash="existing-hash", role="user")
    app.dependency_overrides[get_db] = lambda: session

    async def request_registration():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.post("/api/auth/register", json={"email": "driver@example.com", "password": "a-long-test-password"})

    try:
        response = asyncio.run(request_registration())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "duplicate_email"
    assert session.user is None


def test_registration_cannot_assign_admin_role():
    async def request_registration():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.post(
                "/api/auth/register",
                json={"email": "driver@example.com", "password": "a-long-test-password", "role": "admin"},
            )

    response = asyncio.run(request_registration())
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_invalid_login_credentials_return_generic_unauthorized_response():
    session = FakeSession()
    app.dependency_overrides[get_db] = lambda: session

    async def request_login():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.post(
                "/api/auth/login",
                json={"email": "missing@example.com", "password": "unknown-password"},
            )

    try:
        response = asyncio.run(request_login())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"
    assert "not found" not in response.text.lower()
