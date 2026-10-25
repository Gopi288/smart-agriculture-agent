"""Administrative account management utility for Smart Agriculture Agent.

Allows system administrators to provision admin-level accounts securely
from the terminal without hardcoding credentials or exposing secrets in code.
"""

import argparse
import getpass
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.models.database import create_user, get_user_by_username_or_email, init_db
from config import get_config


def main():
    parser = argparse.ArgumentParser(description="Create a system administrator account")
    parser.add_argument("--username", type=str, help="Administrator username")
    parser.add_argument("--email", type=str, help="Administrator email address")
    parser.add_argument("--name", type=str, default="System Administrator", help="Display name")
    parser.add_argument("--password", type=str, help="Password (optional, will prompt securely if omitted)")
    args = parser.parse_args()

    config = get_config()
    db_path = Path(config.DATABASE_PATH)
    init_db(db_path)

    username = args.username
    if not username:
        username = input("Enter admin username: ").strip()

    email = args.email
    if not email:
        email = input("Enter admin email address: ").strip()

    # Check if user already exists
    existing = get_user_by_username_or_email(db_path, username)
    if existing:
        print(f"[!] Error: An account with username '{username}' already exists.")
        sys.exit(1)

    existing_email = get_user_by_username_or_email(db_path, email)
    if existing_email:
        print(f"[!] Error: An account with email '{email}' already exists.")
        sys.exit(1)

    password = args.password
    if not password:
        password = getpass.getpass("Enter secure password (min 8 characters): ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("[!] Error: Passwords do not match.")
            sys.exit(1)

    if len(password) < 8:
        print("[!] Error: Password must be at least 8 characters.")
        sys.exit(1)

    try:
        user_id = create_user(
            db_path=db_path,
            username=username,
            email=email,
            password=password,
            full_name=args.name,
            role="admin",
        )
        print(f"[*] Successfully provisioned administrator account ID #{user_id} ({username}).")
    except Exception as exc:
        print(f"[!] Database error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
