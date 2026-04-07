from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timezone
from app.database import get_db
from app.models.announcement import Announcement
from app.dependencies import require_editor
from pydantic import BaseModel, ConfigDict
from uuid import UUID
import uuid as _uuid

router = APIRouter(tags=["announcements"])


class AnnouncementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title_uz: str
    title_ru: str
    title_en: str
    content_uz: Optional[str] = None
    content_ru: Optional[str] = None
    content_en: Optional[str] = None
    is_active: bool
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime


class AnnouncementCreate(BaseModel):
    title_uz: str
    title_ru: str
    title_en: str
    content_uz: Optional[str] = None
    content_ru: Optional[str] = None
    content_en: Optional[str] = None
    is_active: bool = True
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


@router.get("/api/announcements", response_model=List[AnnouncementRead])
async def get_active_announcements(db: AsyncSession = Depends(get_db)) -> list:
    """Public: get currently active (non-expired) announcements."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Announcement)
        .where(
            Announcement.is_active == True,
        )
        .order_by(Announcement.created_at.desc())
    )
    all_items = result.scalars().all()
    # Filter in Python to handle None dates cleanly
    active = []
    for ann in all_items:
        if ann.published_at and ann.published_at > now:
            continue
        if ann.expires_at and ann.expires_at < now:
            continue
        active.append(ann)
    return active


@router.get("/api/admin/announcements", response_model=List[AnnouncementRead])
async def admin_list_announcements(
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> list:
    """Admin: list all announcements."""
    result = await db.execute(
        select(Announcement).order_by(Announcement.created_at.desc())
    )
    return result.scalars().all()


@router.post(
    "/api/admin/announcements",
    response_model=AnnouncementRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_announcement(
    data: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> Announcement:
    ann = Announcement(id=_uuid.uuid4(), **data.model_dump())
    db.add(ann)
    await db.flush()
    await db.refresh(ann)
    return ann


@router.put("/api/admin/announcements/{announcement_id}", response_model=AnnouncementRead)
async def update_announcement(
    announcement_id: UUID,
    data: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> Announcement:
    result = await db.execute(
        select(Announcement).where(Announcement.id == announcement_id)
    )
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    for k, v in data.model_dump().items():
        setattr(ann, k, v)
    await db.flush()
    await db.refresh(ann)
    return ann


@router.delete(
    "/api/admin/announcements/{announcement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_announcement(
    announcement_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> None:
    result = await db.execute(
        select(Announcement).where(Announcement.id == announcement_id)
    )
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    await db.delete(ann)
