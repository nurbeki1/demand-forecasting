"""
Settings API Routes
User-specific settings persistence
"""

import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import User, UserSettings
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])

DEFAULT_SETTINGS = {
    "profile": {
        "fullName": "",
        "email": "",
        "language": "kk",
    },
    "forecast": {
        "defaultHorizon": 7,
        "showConfidence": True,
        "showExplanation": True,
        "dataFreshness": None,
        "modelType": "auto",
    },
    "chat": {
        "responseStyle": "analytical",
        "showSuggestions": True,
        "proactiveInsights": True,
    },
    "trust": {
        "showConfidenceLevel": True,
        "showExplanations": True,
        "showDataSources": True,
    },
    "ui": {
        "theme": "dark",
        "compactMode": False,
        "animations": True,
    },
    "notifications": {
        "demandIncrease": True,
        "demandDecrease": True,
        "forecastChange": True,
        "emailNotifications": False,
    },
}


@router.get("")
def get_settings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get current user settings (returns defaults if none saved)"""
    row = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not row:
        settings = dict(DEFAULT_SETTINGS)
        settings["profile"]["email"] = user.email
        settings["profile"]["fullName"] = user.full_name or ""
        return settings

    try:
        return json.loads(row.settings_json)
    except json.JSONDecodeError:
        return DEFAULT_SETTINGS


@router.put("")
def update_all_settings(
    body: Dict[str, Any],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Replace all settings"""
    row = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    settings_str = json.dumps(body)

    if row:
        row.settings_json = settings_str
    else:
        row = UserSettings(user_id=user.id, settings_json=settings_str)
        db.add(row)

    db.commit()
    return body


class SectionUpdate(BaseModel):
    values: Dict[str, Any]


@router.patch("/{section}")
def update_section(
    section: str,
    body: SectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a specific section of settings"""
    row = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()

    if row:
        try:
            settings = json.loads(row.settings_json)
        except json.JSONDecodeError:
            settings = dict(DEFAULT_SETTINGS)
    else:
        settings = dict(DEFAULT_SETTINGS)
        settings["profile"]["email"] = user.email

    if section not in settings:
        settings[section] = {}

    settings[section].update(body.values)
    settings_str = json.dumps(settings)

    if row:
        row.settings_json = settings_str
    else:
        row = UserSettings(user_id=user.id, settings_json=settings_str)
        db.add(row)

    db.commit()
    return settings


@router.delete("")
def reset_settings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Reset settings to defaults"""
    row = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if row:
        db.delete(row)
        db.commit()
    return {"message": "Settings reset to defaults"}
