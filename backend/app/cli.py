"""Interactive operator commands for one-time administrative setup."""

import getpass
import sys

from pydantic import ValidationError

from app.core.database import SessionLocal
from app.schemas.user import RegisterRequest
from app.services.auth import (
    AdminAlreadyProvisionedError,
    DuplicateEmailError,
    provision_initial_admin,
)


def create_admin() -> int:
    email = input("Administrator email: ").strip()
    password = getpass.getpass("Administrator password (12+ characters): ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        print("Passwords did not match.", file=sys.stderr)
        return 2

    try:
        payload = RegisterRequest(email=email, password=password)
    except ValidationError as exc:
        print(f"Invalid administrator details: {exc.errors()[0]['msg']}", file=sys.stderr)
        return 2

    try:
        with SessionLocal() as session:
            provision_initial_admin(payload, session)
    except AdminAlreadyProvisionedError:
        print("An administrator is already provisioned; no changes were made.", file=sys.stderr)
        return 1
    except DuplicateEmailError:
        print("That email already belongs to an account; no changes were made.", file=sys.stderr)
        return 1

    print("Administrator account created.")
    return 0


def main() -> int:
    if sys.argv[1:] == ["create-admin"]:
        return create_admin()
    print("Usage: python -m app.cli create-admin", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
