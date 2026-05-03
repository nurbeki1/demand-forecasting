from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ===== Email Verification =====
class SendCodeRequest(BaseModel):
    """Request to send verification code to email"""
    email: EmailStr


class VerifyCodeRequest(BaseModel):
    """Request to verify the code sent to email"""
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class CompleteRegistrationRequest(BaseModel):
    """Request to complete registration after verification"""
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=8, max_length=128)


# ===== Standard Auth =====
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool = False
    email: Optional[str] = None


class TokenPairResponse(BaseModel):
    """Response with both access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_admin: bool = False
    email: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    is_admin: bool
    is_verified: bool = True
    subscription_plan: str = "free"
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    is_onboarding_completed: bool = False


def user_model_to_response(user) -> UserResponse:
    """Map SQLAlchemy User ORM object to API response."""
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_verified=user.is_verified,
        subscription_plan=getattr(user, "subscription_plan", None) or "free",
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        is_onboarding_completed=bool(getattr(user, "is_onboarding_completed", False)),
    )


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None


# ===== Google OAuth =====
class GoogleAuthRequest(BaseModel):
    """Google OAuth token from frontend"""
    credential: str  # Google ID token


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
    success: bool = True


class MockSubscribeRequest(BaseModel):
    """Demo checkout — no real payment processor."""

    plan: str = Field(default="pro", pattern="^(pro|enterprise)$")
