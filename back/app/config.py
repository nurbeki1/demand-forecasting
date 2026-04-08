"""
Centralized configuration with Pydantic Settings.
Validates environment variables at startup.
"""
import sys
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""

    # JWT Configuration - REQUIRED
    jwt_secret_key: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT tokens. Must be at least 32 characters."
    )

    # Token expiration
    access_token_expire_minutes: int = Field(
        default=1440,
        ge=1,
        le=10080,
        description="Access token expiration time in minutes (default: 1440 = 24 hours)"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Refresh token expiration time in days (default: 7)"
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable/disable rate limiting"
    )
    rate_limit_auth_per_minute: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Rate limit for auth endpoints per minute"
    )
    rate_limit_chat_per_minute: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Rate limit for chat endpoint per minute"
    )
    rate_limit_default_per_minute: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Default rate limit per minute"
    )

    # CORS
    cors_origins: Optional[str] = Field(
        default=None,
        description="Comma-separated list of additional CORS origins"
    )

    # OpenAI
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for AI chat"
    )

    # Database
    database_url: Optional[str] = Field(
        default=None,
        description="Database connection URL"
    )

    # Google OAuth
    google_client_id: Optional[str] = Field(
        default=None,
        description="Google OAuth Client ID"
    )

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret is not a placeholder value."""
        placeholder_values = [
            "CHANGE_ME_SUPER_SECRET",
            "your_jwt_secret_key_here",
            "secret",
            "changeme",
            "your-secret-key",
        ]
        if v.lower() in [p.lower() for p in placeholder_values]:
            raise ValueError(
                "JWT_SECRET_KEY must not be a placeholder value. "
                "Generate a secure key with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
            )
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def validate_settings_on_startup() -> Settings:
    """
    Validate settings at application startup.
    Exits with error if configuration is invalid.
    """
    try:
        settings = Settings()
        print("[Config] Settings validated successfully")
        print(f"[Config] Access token expire: {settings.access_token_expire_minutes} minutes")
        print(f"[Config] Refresh token expire: {settings.refresh_token_expire_days} days")
        print(f"[Config] Rate limiting: {'enabled' if settings.rate_limit_enabled else 'disabled'}")
        return settings
    except Exception as e:
        print(f"[Config] FATAL: Configuration validation failed!")
        print(f"[Config] Error: {e}")
        print("\n[Config] Required environment variables:")
        print("  - JWT_SECRET_KEY: Must be at least 32 characters (not a placeholder)")
        print("\n[Config] Generate a secure secret with:")
        print('  python -c "import secrets; print(secrets.token_urlsafe(64))"')
        sys.exit(1)
