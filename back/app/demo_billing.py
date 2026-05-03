"""Demo-only subscription unlock (no real payment gateway)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import User
from app.schemas import MockSubscribeRequest, UserResponse, user_model_to_response


def apply_mock_subscription(db: Session, user: User, data: MockSubscribeRequest) -> UserResponse:
    """Set subscription_plan to paid after mock checkout."""
    _ = data.plan
    user.subscription_plan = "paid"
    db.commit()
    db.refresh(user)
    return user_model_to_response(user)
