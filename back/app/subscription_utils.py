"""Subscription helpers for ML model access."""

from __future__ import annotations

from typing import FrozenSet

from fastapi import HTTPException

ALLOWED_MODELS_FREE: FrozenSet[str] = frozenset({"random_forest"})
ALLOWED_MODELS_FULL: FrozenSet[str] = frozenset({
    "random_forest",
    "lightgbm",
    "xgboost",
})


def allowed_ml_models_for_user(user) -> FrozenSet[str]:
    """Paid/pro subscribers get full model set; everyone else (including admins) RF-only unless subscribed."""
    raw = getattr(user, "subscription_plan", None) or "free"
    plan = str(raw).strip().lower()
    if plan in ("paid", "pro", "subscriber"):
        return ALLOWED_MODELS_FULL
    return ALLOWED_MODELS_FREE


def enforce_chat_model_type(user, model_type: str) -> str:
    if model_type not in ALLOWED_MODELS_FULL:
        raise HTTPException(
            status_code=400,
            detail="Unknown model_type; use random_forest, lightgbm, or xgboost.",
        )
    allowed = allowed_ml_models_for_user(user)
    if model_type not in allowed:
        raise HTTPException(
            status_code=403,
            detail=(
                "Бұл ML моделі жазылымға арналған. Тегін тарифте тек Random Forest қолданылады."
            ),
        )
    return model_type
