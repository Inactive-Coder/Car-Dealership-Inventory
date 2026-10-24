import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.user import User
from app.models.vehicle import Vehicle


@pytest.mark.integration
def test_concurrent_purchases_never_oversell(postgres_test_session_factory):
    sessions = postgres_test_session_factory
    account = User(
        email=f"buyer-{uuid4()}@example.com",
        password_hash=hash_password("integration-test-password"),
        role="user",
        created_at=datetime.now(timezone.utc),
    )
    vehicle = Vehicle(make="Test", model="Car", category="Sedan", price=Decimal("100.00"), quantity=1)
    with sessions() as session:
        session.add_all([account, vehicle])
        session.commit()
        session.refresh(account)
        session.refresh(vehicle)

    token, _ = create_access_token(str(account.id), account.role)
    def override_db():
        session = sessions()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db

    async def make_two_purchases():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            headers = {"Authorization": f"Bearer {token}"}
            return await asyncio.gather(
                client.post(f"/api/vehicles/{vehicle.id}/purchase", headers=headers),
                client.post(f"/api/vehicles/{vehicle.id}/purchase", headers=headers),
            )

    try:
        responses = asyncio.run(make_two_purchases())
    finally:
        app.dependency_overrides.clear()

    with sessions() as session:
        remaining = session.scalar(select(Vehicle.quantity).where(Vehicle.id == vehicle.id))
        session.delete(session.get(Vehicle, vehicle.id))
        session.delete(session.get(User, account.id))
        session.commit()

    assert sorted(response.status_code for response in responses) == [200, 409]
    assert remaining == 0
