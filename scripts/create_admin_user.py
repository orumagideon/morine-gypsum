#!/usr/bin/env python3
"""Create or update an AdminUser with email and password.

Usage:
    python scripts/create_admin_user.py --email admin@example.com --password secret

This script is safe to run multiple times; it will update password if the user exists.
"""
import argparse
from sqlmodel import Session, select
from app.db.session import engine
from app.models.models import AdminUser

# Import the hashing helper from auth_router to keep hashing consistent
from app.routers.auth_router import get_password_hash


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True, help="Admin email/identifier")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--username", help="Optional username; defaults to email")
    args = parser.parse_args()

    # Use the project's DB engine (imported as `engine`)

    identifier = args.email
    username = args.username or args.email

    with Session(engine) as session:
        # Try to find by username or email
        admin = session.exec(select(AdminUser).where((AdminUser.username == identifier) | (AdminUser.email == identifier))).first()
        if admin:
            print(f"Updating admin (id={admin.id})")
            admin.password_hash = get_password_hash(args.password)
            # ensure email/username set
            admin.email = args.email
            admin.username = username
            session.add(admin)
            session.commit()
            session.refresh(admin)
            print(f"Updated admin id={admin.id}, username={admin.username}, email={admin.email}")
        else:
            admin = AdminUser(username=username, email=args.email, password_hash=get_password_hash(args.password))
            session.add(admin)
            session.commit()
            session.refresh(admin)
            print(f"Created admin id={admin.id}, username={admin.username}, email={admin.email}")


if __name__ == "__main__":
    main()
