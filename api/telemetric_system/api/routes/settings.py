"""Admin settings endpoints.

Provides:
- GET /settings: get all public settings as key-value map
- GET /settings/company: get company-specific settings
- PUT /settings: update settings (admin only)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from telemetric_system.core.database.connection import get_session
from telemetric_system.models.admin_settings import AdminSettings
from telemetric_system.api.middleware.auth import authenticate_request, require_roles

router = APIRouter(prefix="/settings", tags=["settings"])

# Default company settings
_DEFAULTS = {
    "company_name": "Fleet Manager",
    "company_logo_url": None,
    "timezone": "Africa/Nairobi",
    "currency": "KES",
    "date_format": "DD/MM/YYYY",
    "speed_unit": "kph",
    "distance_unit": "km",
}


def _get_settings_dict(session) -> Dict[str, Any]:
    rows = session.query(AdminSettings).filter(AdminSettings.is_deleted.is_(False)).all()
    result = dict(_DEFAULTS)
    for row in rows:
        result[row.key] = row.value
    return result


@router.get("", summary="Get all settings")
def get_settings(request: Request):
    _ = authenticate_request(dict(request.headers))
    session = get_session()
    try:
        return _get_settings_dict(session)
    finally:
        session.close()


@router.get("/company", summary="Get company settings")
def get_company_settings(request: Request):
    _ = authenticate_request(dict(request.headers))
    session = get_session()
    try:
        settings = _get_settings_dict(session)
        return {
            "id": 1,
            "company_name": settings.get("company_name", "Fleet Manager"),
            "company_logo_url": settings.get("company_logo_url"),
            "timezone": settings.get("timezone", "Africa/Nairobi"),
            "currency": settings.get("currency", "KES"),
        }
    finally:
        session.close()


class SettingsUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=128)
    company_logo_url: Optional[str] = Field(None, max_length=512)
    timezone: Optional[str] = Field(None, max_length=64)
    currency: Optional[str] = Field(None, max_length=10)
    date_format: Optional[str] = Field(None, max_length=32)
    speed_unit: Optional[str] = Field(None, max_length=10)
    distance_unit: Optional[str] = Field(None, max_length=10)


@router.put("", summary="Update settings")
def update_settings(request: Request, payload: SettingsUpdate):
    require_roles(dict(request.headers), "admin")
    session = get_session()
    try:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if value is None:
                continue
            row = session.query(AdminSettings).filter(AdminSettings.key == key).one_or_none()
            if row:
                row.value = str(value)
                session.add(row)
            else:
                row = AdminSettings(key=key, value=str(value), is_public=True, category="company")
                session.add(row)
        session.commit()
        return _get_settings_dict(session)
    finally:
        session.close()
