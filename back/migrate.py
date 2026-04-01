"""
Database Migration Script
Run this once to add missing columns to production database
"""
import os
from sqlalchemy import create_engine, text, inspect

# Load env
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    exit(1)

# Fix postgres:// -> postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def run_migrations():
    with engine.connect() as conn:
        inspector = inspect(engine)

        # Check if users table exists
        if 'users' not in inspector.get_table_names():
            print("Creating users table...")
            conn.execute(text("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR UNIQUE NOT NULL,
                    hashed_password VARCHAR,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    is_verified BOOLEAN DEFAULT FALSE,
                    google_id VARCHAR UNIQUE,
                    avatar_url VARCHAR,
                    full_name VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            print("Users table created!")
        else:
            # Add missing columns to users table
            existing_columns = [col['name'] for col in inspector.get_columns('users')]

            migrations = [
                ("is_verified", "ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"),
                ("google_id", "ALTER TABLE users ADD COLUMN google_id VARCHAR UNIQUE"),
                ("avatar_url", "ALTER TABLE users ADD COLUMN avatar_url VARCHAR"),
                ("full_name", "ALTER TABLE users ADD COLUMN full_name VARCHAR"),
            ]

            for col_name, sql in migrations:
                if col_name not in existing_columns:
                    print(f"Adding column: {col_name}")
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"Added {col_name}!")
                else:
                    print(f"Column {col_name} already exists")

        # Check if verification_codes table exists
        if 'verification_codes' not in inspector.get_table_names():
            print("Creating verification_codes table...")
            conn.execute(text("""
                CREATE TABLE verification_codes (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR NOT NULL,
                    code VARCHAR NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_used BOOLEAN DEFAULT FALSE
                )
            """))
            conn.execute(text("CREATE INDEX ix_verification_codes_email ON verification_codes(email)"))
            conn.commit()
            print("Verification codes table created!")
        else:
            print("Verification codes table already exists")

        print("\nMigration complete!")

if __name__ == "__main__":
    run_migrations()
