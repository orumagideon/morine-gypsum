#!/usr/bin/env python3
"""Create or reset the admin user (idempotent).

Usage (from project root, venv active):
    python scripts/reset_admin.py
    python scripts/reset_admin.py --email admin@morinegypsum.co.ke --password 'Admin@12345'
    python scripts/reset_admin.py --prompt        # ask for the password interactively

Reads DATABASE_URL from the environment / .env (via app.db.session).
Hashing uses app.routers.auth_router.get_password_hash (passlib bcrypt).
The AdminUser model has no is_admin/is_superuser columns: every AdminUser is an admin.
"""
import argparse
import getpass
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, SQLModel, select  # noqa: E402

from app.db.session import engine  # noqa: E402
from app.models.models import AdminUser  # noqa: E402
from app.routers.auth_router import get_password_hash  # noqa: E402

DEFAULT_EMAIL = "admin@morinegypsum.co.ke"
DEFAULT_PASSWORD = "Admin@12345"


def main():
    parser = argparse.ArgumentParser(description="Create or reset the admin user")
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--username", help="Defaults to the email")
    parser.add_argument("--password", default=None)
    parser.add_argument("--prompt", action="store_true", help="Prompt for the password")
    args = parser.parse_args()

    password = args.password
    if args.prompt:
        password = getpass.getpass("New admin password: ")
        if password != getpass.getpass("Confirm password: "):
            sys.exit("Passwords do not match")
    password = password or DEFAULT_PASSWORD
    username = args.username or args.email

    SQLModel.metadata.create_all(engine, tables=[AdminUser.__table__])

    with Session(engine) as session:
        admin = session.exec(
            select(AdminUser).where(
                (AdminUser.email == args.email)
                | (AdminUser.username == username)
                | (AdminUser.username == args.email)
            )
        ).first()
        action = "Updated"
        if admin is None:
            admin = AdminUser(username=username, email=args.email, password_hash="")
            action = "Created"
        admin.password_hash = get_password_hash(password)
        admin.is_verified = True
        admin.email = args.email
        admin.otp_hash = None
        admin.otp_expires_at = None
        admin.reset_token_hash = None
        admin.reset_token_expires_at = None
        session.add(admin)
        session.commit()
        session.refresh(admin)
        print(f"{action} admin id={admin.id} username={admin.username} email={admin.email}")


if __name__ == "__main__":
    main()
