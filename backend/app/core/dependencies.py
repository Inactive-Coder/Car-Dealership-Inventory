from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AuthenticationError
    try:
        claims = decode_access_token(credentials.credentials)
        user_id = UUID(str(claims["sub"]))
    except (ValueError, TypeError, KeyError, jwt.PyJWTError) as exc:
        # Invalid signatures, malformed claims, and expired tokens share one response.
        raise AuthenticationError from exc
    user = session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise AuthenticationError
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise AuthorizationError
    return user
