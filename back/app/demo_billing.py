"""Demo-only subscription unlock (no real payment gateway)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import User
from app.schemas import MockSubscribeRequest, UserResponse


def apply_mock_subscription(db: Session, user: User, data: MockSubscribeRequest) -> UserResponse:
    """Set subscription_plan to paid after mock checkout."""
    _ = data.plan
    user.subscription_plan = "paid"
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_verified=user.is_verified,
        subscription_plan=getattr(user, "subscription_plan", None) or "paid",
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
    )
