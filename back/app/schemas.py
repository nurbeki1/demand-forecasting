from pydantic import BaseModel, EmailStr, Field
from typing import Optional


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
    password: str = Field(min_length=4, max_length=128)


# ===== Standard Auth =====
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool = False


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    is_admin: bool
    is_verified: bool = True
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


# ===== Google OAuth =====
class GoogleAuthRequest(BaseModel):
    """Google OAuth token from frontend"""
    credential: str  # Google ID token


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
    success: bool = True
