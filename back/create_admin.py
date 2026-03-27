#!/usr/bin/env python3
"""
Script to create an admin user.
Usage: python create_admin.py admin@example.com password123
"""

import sys
from app.database import SessionLocal, engine, Base
from app.models import User
from app.security import hash_password

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


def create_admin(email: str, password: str):
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            if existing.is_admin:
                print(f"User {email} is already an admin.")
            else:
                existing.is_admin = True
                db.commit()
                print(f"User {email} has been promoted to admin.")
            return

        # Create new admin user
        user = User(
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
            is_admin=True,
        )
        db.add(user)
        db.commit()
        print(f"Admin user created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_admin.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    create_admin(email, password)
