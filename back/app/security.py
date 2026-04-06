"""
Security utilities for authentication and JWT handling.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple

from jose import jwt, JWTError
from passlib.context import CryptContext

from .config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    """
    Create an access token.

    Args:
        subject: Token subject (usually user email)
        expires_minutes: Custom expiration time in minutes

    Returns:
        Encoded JWT access token
    """
    settings = get_settings()
    expire_minutes = expires_minutes or settings.access_token_expire_minutes
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)

    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)


def create_refresh_token(subject: str, expires_days: Optional[int] = None) -> str:
    """
    Create a refresh token.

    Args:
        subject: Token subject (usually user email)
        expires_days: Custom expiration time in days

    Returns:
        Encoded JWT refresh token
    """
    settings = get_settings()
    expire_days = expires_days or settings.refresh_token_expire_days
    expire = datetime.utcnow() + timedelta(days=expire_days)

    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)


def create_token_pair(subject: str) -> Tuple[str, str]:
    """
    Create both access and refresh tokens.

    Args:
        subject: Token subject (usually user email)

    Returns:
        Tuple of (access_token, refresh_token)
    """
    access_token = create_access_token(subject)
    refresh_token = create_refresh_token(subject)
    return access_token, refresh_token


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        JWTError: If token is invalid or expired
    """
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])


def verify_refresh_token(token: str) -> Optional[str]:
    """
    Verify a refresh token and return the subject.

    Args:
        token: Refresh token string

    Returns:
        Subject (user email) if valid, None otherwise
    """
    try:
        payload = decode_token(token)

        # Check token type
        if payload.get("type") != "refresh":
            return None

        return payload.get("sub")
    except JWTError:
        return None
