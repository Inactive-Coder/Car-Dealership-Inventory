from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.user import LoginRequest, RegisterRequest


class DuplicateEmailError(Exception):
    """Raised when a normalized email address is already registered."""


class InvalidCredentialsError(Exception):
    """Raised without disclosing which credential was incorrect."""


class AdminAlreadyProvisionedError(Exception):
    """Raised when an administrator already exists; bootstrap never replaces one."""


def register_user(payload: RegisterRequest, session: Session) -> User:
    normalized_email = str(payload.email).strip().lower()
    existing = session.scalar(select(User).where(User.email == normalized_email))
    if existing is not None:
        raise DuplicateEmailError

    user = User(
        email=normalized_email,
        password_hash=hash_password(payload.password),
        role=UserRole.USER.value,
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise DuplicateEmailError from exc
    session.refresh(user)
    return user


def authenticate_user(payload: LoginRequest, session: Session) -> tuple[User, str, int]:
    normalized_email = str(payload.email).strip().lower()
    user = session.scalar(select(User).where(User.email == normalized_email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise InvalidCredentialsError
    token, expires_in = create_access_token(str(user.id), user.role)
    return user, token, expires_in


def provision_initial_admin(payload: RegisterRequest, session: Session) -> User:
    admin_id = session.scalar(select(User.id).where(User.role == UserRole.ADMIN.value).limit(1))
    if admin_id is not None:
        raise AdminAlreadyProvisionedError

    normalized_email = str(payload.email).strip().lower()
    existing = session.scalar(select(User.id).where(User.email == normalized_email))
    if existing is not None:
        raise DuplicateEmailError

    user = User(
        email=normalized_email,
        password_hash=hash_password(payload.password),
        role=UserRole.ADMIN.value,
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        admin_id = session.scalar(select(User.id).where(User.role == UserRole.ADMIN.value).limit(1))
        if admin_id is not None:
            raise AdminAlreadyProvisionedError from exc
        raise DuplicateEmailError from exc
    session.refresh(user)
    return user
