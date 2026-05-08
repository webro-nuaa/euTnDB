from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.models import SystemSetting, User
from app.schemas.common import ApiResponse
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/admin/settings", tags=["Admin Settings"])


class SettingItem(BaseModel):
    key: str
    value: Optional[str] = None


class SettingsUpdate(BaseModel):
    settings: list[SettingItem]


class TestEmailRequest(BaseModel):
    test_email: str


DEFAULT_SETTINGS = {
    "site_name": "euTnDB",
    "site_description": "DNA Transposon Database",
    "default_status": "pending",
    "blast_enabled": "true",
    "minetn_enabled": "true",
    "max_upload_size": "100",
    "max_download_entries": "50",
    "smtp_host": "",
    "smtp_port": "465",
    "smtp_user": "",
    "smtp_password": "",
    "smtp_from_name": "euTnDB",
    "smtp_use_ssl": "true",
}


@router.get("")
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(select(SystemSetting))
    db_settings = result.scalars().all()

    settings_map = {}
    for s in db_settings:
        settings_map[s.key] = s.value if s.value is not None else ""

    all_settings = {}
    for key, default_val in DEFAULT_SETTINGS.items():
        all_settings[key] = settings_map.get(key, default_val)

    return ApiResponse(data=all_settings)


@router.put("")
async def update_settings(
    data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    for item in data.settings:
        result = await db.execute(
            select(SystemSetting).where(SystemSetting.key == item.key)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.value = item.value
        else:
            db.add(SystemSetting(key=item.key, value=item.value))

    await db.commit()

    await _reload_smtp_settings(db)

    return ApiResponse(data=None, message="Settings saved successfully")


@router.post("/test-email")
async def test_email(
    data: TestEmailRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    await _reload_smtp_settings(db)

    from app.core.email import send_email
    success = send_email(
        to_email=data.test_email,
        subject="euTnDB Email Test",
        body_html="""
        <div style="font-family: Arial, sans-serif; max-width: 400px; margin: 0 auto;">
          <div style="background: #1a73e8; color: white; padding: 16px; border-radius: 8px 8px 0 0;">
            <h3 style="margin: 0;">euTnDB Email Test</h3>
          </div>
          <div style="padding: 16px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;">
            <p>If you received this email, your SMTP settings are configured correctly.</p>
          </div>
        </div>
        """
    )

    if success:
        return ApiResponse(data=None, message="Test email sent successfully")
    else:
        raise HTTPException(status_code=500, detail="Failed to send email. Please check your SMTP settings.")


async def _reload_smtp_settings(db: AsyncSession):
    from app.core.config import settings as app_settings

    result = await db.execute(select(SystemSetting))
    db_settings = result.scalars().all()

    settings_map = {}
    for s in db_settings:
        settings_map[s.key] = s.value if s.value is not None else ""

    if settings_map.get("smtp_host"):
        app_settings.SMTP_HOST = settings_map["smtp_host"]
    else:
        app_settings.SMTP_HOST = ""
    if settings_map.get("smtp_port"):
        try:
            app_settings.SMTP_PORT = int(settings_map["smtp_port"])
        except ValueError:
            app_settings.SMTP_PORT = 465
    if settings_map.get("smtp_user"):
        app_settings.SMTP_USER = settings_map["smtp_user"]
    else:
        app_settings.SMTP_USER = ""
    if settings_map.get("smtp_password"):
        app_settings.SMTP_PASSWORD = settings_map["smtp_password"]
    else:
        app_settings.SMTP_PASSWORD = ""
    if settings_map.get("smtp_from_name"):
        app_settings.SMTP_FROM_NAME = settings_map["smtp_from_name"]
    else:
        app_settings.SMTP_FROM_NAME = "euTnDB"
    use_ssl_val = settings_map.get("smtp_use_ssl", "true")
    app_settings.SMTP_USE_SSL = use_ssl_val.lower() == "true"
