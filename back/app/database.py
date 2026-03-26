import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Use DATABASE_URL from environment (Neon PostgreSQL) or fallback to SQLite for local dev
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Neon/PostgreSQL - fix for SQLAlchemy (postgres:// -> postgresql://)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)
else:
    # Local development - SQLite
    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "app.db")
    DB_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass
