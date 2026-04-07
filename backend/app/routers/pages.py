from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.page import Page
from app.dependencies import require_editor
from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/api/pages", tags=["pages"])


class PageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title_uz: str
    title_ru: str
    title_en: str
    content_uz: Optional[str] = None
    content_ru: Optional[str] = None
    content_en: Optional[str] = None
    is_published: bool
    meta_description: Optional[str] = None
    updated_at: datetime


class PageCreate(BaseModel):
    slug: str
    title_uz: str
    title_ru: str
    title_en: str
    content_uz: Optional[str] = None
    content_ru: Optional[str] = None
    content_en: Optional[str] = None
    is_published: bool = False
    meta_description: Optional[str] = None


@router.get("", response_model=list[PageRead])
async def list_pages_admin(
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> list:
    """Admin: list all pages (published and unpublished)."""
    result = await db.execute(
        select(Page).order_by(Page.slug)
    )
    return result.scalars().all()


@router.get("/{slug}", response_model=PageRead)
async def get_page(slug: str, db: AsyncSession = Depends(get_db)) -> Page:
    """Get a static page by slug."""
    result = await db.execute(
        select(Page).where(Page.slug == slug, Page.is_published == True)
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    return page


@router.post("", response_model=PageRead, status_code=status.HTTP_201_CREATED)
async def create_page(
    data: PageCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> Page:
    """Create a new static page."""
    import uuid as _uuid
    existing = await db.execute(select(Page).where(Page.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already exists")

    page = Page(id=_uuid.uuid4(), **data.model_dump())
    db.add(page)
    await db.flush()
    await db.refresh(page)
    return page


@router.put("/{slug}", response_model=PageRead)
async def update_page(
    slug: str,
    data: PageCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> Page:
    """Update a static page."""
    result = await db.execute(select(Page).where(Page.slug == slug))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    for field, value in data.model_dump().items():
        setattr(page, field, value)

    await db.flush()
    await db.refresh(page)
    return page
