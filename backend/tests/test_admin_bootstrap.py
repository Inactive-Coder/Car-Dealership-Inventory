from datetime import datetime, timezone
from uuid import UUID

import pytest

from app.core.security import verify_password
from app.models.user import User
from app.schemas.user import RegisterRequest
from app.services.auth import AdminAlreadyProvisionedError, provision_initial_admin


class FakeSession:
    def __init__(self, scalar_results):
        self.scalar_results = list(scalar_results)
        self.added = None
        self.committed = False

    def scalar(self, _statement):
        return self.scalar_results.pop(0)

    def add(self, user):
        self.added = user

    def commit(self):
        self.committed = True

    def refresh(self, user):
        user.id = UUID("f4f7f507-625b-4f6b-a4fa-6a1f51986a59")
        user.created_at = datetime.now(timezone.utc)

    def rollback(self):
        pass


def test_initial_admin_is_created_with_hashed_password():
    session = FakeSession([None, None])
    account = provision_initial_admin(
        RegisterRequest(email="admin@example.com", password="a-strong-admin-password"),
        session,
    )

    assert account.role == "admin"
    assert account.email == "admin@example.com"
    assert verify_password("a-strong-admin-password", account.password_hash)
    assert session.committed


def test_admin_bootstrap_is_idempotent_after_first_admin_exists():
    session = FakeSession([UUID("f4f7f507-625b-4f6b-a4fa-6a1f51986a59")])
    with pytest.raises(AdminAlreadyProvisionedError):
        provision_initial_admin(
            RegisterRequest(email="admin@example.com", password="a-strong-admin-password"),
            session,
        )

    assert session.added is None
    assert not session.committed
