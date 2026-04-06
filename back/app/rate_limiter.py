"""
Rate limiting configuration using SlowAPI.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

from .config import get_settings


def get_key_func(request: Request) -> str:
    """
    Get rate limit key: user ID if authenticated, otherwise IP address.
    """
    # Try to get user from request state (set by auth middleware)
    user = getattr(request.state, "user", None)
    if user and hasattr(user, "id"):
        return f"user:{user.id}"

    # Fall back to IP address
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_key_func,
    default_limits=["100/minute"],
    enabled=True,  # Will be controlled by settings at runtime
)


# Rate limit constants for easy reference
class RateLimits:
    """Rate limit values for different endpoints."""
    SEND_CODE = "3/minute"
    VERIFY_CODE = "5/minute"
    LOGIN = "5/minute"
    CHAT = "20/minute"
    DEFAULT = "100/minute"
