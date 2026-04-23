from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.home_settings import HomeSettings
from app.dependencies import require_editor
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/home-settings", tags=["home-settings"])


class HomeSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    hero_title: dict
    hero_subtitle: dict
    hero_issn: Optional[str] = None
    hero_video_url: Optional[str] = None
    hero_video_poster_url: Optional[str] = None
    hero_video_active: bool = False
    site_logo_url: Optional[str] = None
    site_name: dict = {}
    site_tagline: dict = {}
    about_title: dict
    about_text: dict
    about_image_url: Optional[str] = None
    issn_online: Optional[str] = None
    issn_print: Optional[str] = None
    license_type: Optional[str] = None
    announcement_uz: Optional[str] = None
    announcement_ru: Optional[str] = None
    announcement_en: Optional[str] = None
    announcement_active: bool = False
    cta_title: dict
    cta_subtitle: dict
    theme: str = "indigo"
    updated_at: datetime


class HomeSettingsUpdate(BaseModel):
    hero_title: Optional[dict] = None
    hero_subtitle: Optional[dict] = None
    hero_issn: Optional[str] = None
    hero_video_url: Optional[str] = None
    hero_video_poster_url: Optional[str] = None
    hero_video_active: Optional[bool] = None
    site_logo_url: Optional[str] = None
    site_name: Optional[dict] = None
    site_tagline: Optional[dict] = None
    about_title: Optional[dict] = None
    about_text: Optional[dict] = None
    about_image_url: Optional[str] = None
    issn_online: Optional[str] = None
    issn_print: Optional[str] = None
    license_type: Optional[str] = None
    announcement_uz: Optional[str] = None
    announcement_ru: Optional[str] = None
    announcement_en: Optional[str] = None
    announcement_active: Optional[bool] = None
    cta_title: Optional[dict] = None
    cta_subtitle: Optional[dict] = None
    theme: Optional[str] = None


@router.get("", response_model=HomeSettingsRead)
async def get_home_settings(db: AsyncSession = Depends(get_db)) -> HomeSettings:
    """Public: get homepage settings."""
    result = await db.execute(select(HomeSettings).where(HomeSettings.id == "default"))
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found")
    return settings


@router.put("", response_model=HomeSettingsRead)
async def update_home_settings(
    data: HomeSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> HomeSettings:
    """Admin: update homepage settings."""
    result = await db.execute(select(HomeSettings).where(HomeSettings.id == "default"))
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)

    await db.flush()
    await db.refresh(settings)
    return settings
