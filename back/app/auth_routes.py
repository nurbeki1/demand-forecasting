"""
Authentication Routes
- Email verification flow
- Google OAuth
- Standard login/register
- Token refresh
"""
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .deps import get_db, get_current_user
from .models import User, VerificationCode
from .schemas import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse,
    SendCodeRequest, VerifyCodeRequest, CompleteRegistrationRequest,
    GoogleAuthRequest, MessageResponse, TokenPairResponse, RefreshTokenRequest
)
from .security import (
    hash_password, verify_password, create_access_token,
    create_token_pair, verify_refresh_token
)
from .email_service import generate_verification_code, send_verification_email, get_code_expiry
from .rate_limiter import limiter, RateLimits

router = APIRouter(prefix="/auth", tags=["auth"])

# Google OAuth Client ID
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")


# ===== EMAIL VERIFICATION FLOW =====

@router.post("/send-code", response_model=MessageResponse)
@limiter.limit(RateLimits.SEND_CODE)
def send_verification_code(
    request: Request,
    data: SendCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Step 1: Send verification code to email
    """
    try:
        # Check if user already exists and is verified
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user and existing_user.is_verified:
            raise HTTPException(status_code=400, detail="Пользователь уже зарегистрирован")

        # Delete any existing codes for this email
        db.query(VerificationCode).filter(
            VerificationCode.email == data.email
        ).delete()
        db.commit()

        # Generate new code
        code = generate_verification_code()

        # Save code to database
        verification = VerificationCode(
            email=data.email,
            code=code,
            expires_at=get_code_expiry()
        )
        db.add(verification)
        db.commit()

        # Send email
        if not send_verification_email(data.email, code):
            raise HTTPException(status_code=500, detail="Не удалось отправить код")

        return MessageResponse(message="Код отправлен на вашу почту")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] send-code failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.post("/verify-code", response_model=MessageResponse)
@limiter.limit(RateLimits.VERIFY_CODE)
def verify_code(
    request: Request,
    data: VerifyCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Step 2: Verify the code
    """
    verification = db.query(VerificationCode).filter(
        VerificationCode.email == data.email,
        VerificationCode.code == data.code,
        VerificationCode.is_used == False
    ).first()

    if not verification:
        raise HTTPException(status_code=400, detail="Неверный код")

    if verification.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Код истёк")

    return MessageResponse(message="Код подтверждён")


@router.post("/complete-registration", response_model=TokenPairResponse)
@limiter.limit(RateLimits.LOGIN)
def complete_registration(
    request: Request,
    data: CompleteRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Step 3: Complete registration with password
    """
    # Verify code again
    verification = db.query(VerificationCode).filter(
        VerificationCode.email == data.email,
        VerificationCode.code == data.code,
        VerificationCode.is_used == False
    ).first()

    if not verification:
        raise HTTPException(status_code=400, detail="Неверный код")

    if verification.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Код истёк")

    # Mark code as used
    verification.is_used = True
    db.commit()

    # Check if user exists
    user = db.query(User).filter(User.email == data.email).first()

    if user:
        # Update existing unverified user
        user.hashed_password = hash_password(data.password)
        user.is_verified = True
    else:
        # Create new user
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            is_verified=True,
            is_admin=False
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    # Create token pair
    access_token, refresh_token = create_token_pair(user.email)
    return TokenPairResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        is_admin=user.is_admin,
        email=user.email
    )


# ===== GOOGLE OAUTH =====

@router.post("/google", response_model=TokenPairResponse)
@limiter.limit(RateLimits.LOGIN)
def google_auth(
    request: Request,
    data: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate with Google OAuth
    """
    if not GOOGLE_CLIENT_ID:
        print("[ERROR] GOOGLE_CLIENT_ID not set")
        raise HTTPException(status_code=500, detail="Google OAuth не настроен")

    try:
        # Verify Google token
        idinfo = id_token.verify_oauth2_token(
            data.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        google_id = idinfo.get("sub")
        full_name = idinfo.get("name")
        avatar_url = idinfo.get("picture")

        if not email:
            raise HTTPException(status_code=400, detail="Email не получен от Google")

        # Find or create user
        user = db.query(User).filter(
            (User.email == email) | (User.google_id == google_id)
        ).first()

        if user:
            # Update Google info
            user.google_id = google_id
            user.full_name = full_name
            user.avatar_url = avatar_url
            user.is_verified = True
        else:
            # Create new user
            user = User(
                email=email,
                google_id=google_id,
                full_name=full_name,
                avatar_url=avatar_url,
                is_verified=True,
                is_admin=False
            )
            db.add(user)

        db.commit()
        db.refresh(user)

        # Create token pair
        access_token, refresh_token = create_token_pair(user.email)
        return TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            is_admin=user.is_admin,
            email=email
        )

    except ValueError as e:
        print(f"[ERROR] Google token validation failed: {e}")
        raise HTTPException(status_code=400, detail="Неверный Google токен")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Google auth failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


# ===== STANDARD AUTH =====

@router.post("/register")
@limiter.limit(RateLimits.LOGIN)
def register(
    request: Request,
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user (regular user, not admin) - Legacy endpoint"""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        is_admin=False,
        is_verified=True,  # Skip verification for legacy endpoint
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Регистрация успешна"}


@router.post("/login", response_model=TokenPairResponse)
@limiter.limit(RateLimits.LOGIN)
def login(
    request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login and get access + refresh tokens"""
    try:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Неверные данные")

        # Check if user has password (not Google-only user)
        if not user.hashed_password:
            raise HTTPException(
                status_code=401,
                detail="Войдите через Google"
            )

        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Неверные данные")

        if not user.is_verified:
            raise HTTPException(status_code=401, detail="Email не подтверждён")

        access_token, refresh_token = create_token_pair(user.email)
        return TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            is_admin=user.is_admin,
            email=user.email
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] login failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.post("/refresh", response_model=TokenPairResponse)
@limiter.limit(RateLimits.LOGIN)
def refresh_token(
    request: Request,
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    Returns new access and refresh token pair.
    """
    # Verify refresh token
    email = verify_refresh_token(data.refresh_token)
    if not email:
        raise HTTPException(
            status_code=401,
            detail="Недействительный или истёкший refresh token"
        )

    # Get user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Аккаунт деактивирован")

    # Create new token pair
    access_token, refresh_token = create_token_pair(user.email)
    return TokenPairResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        is_admin=user.is_admin,
        email=user.email
    )


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_verified=user.is_verified,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
    )
