from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.category import Category
from app.dependencies import require_editor
from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import uuid
import re

router = APIRouter(prefix="/api/categories", tags=["categories"])


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name_uz: str
    name_ru: str
    name_en: str
    slug: str
    order: int
    created_at: datetime


class CategoryCreate(BaseModel):
    name_uz: str
    name_ru: str
    name_en: str
    slug: Optional[str] = None
    order: int = 0

    @field_validator("name_uz", "name_ru", "name_en")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Bo'sh bo'lishi mumkin emas")
        return v.strip()


class CategoryUpdate(BaseModel):
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    slug: Optional[str] = None
    order: Optional[int] = None


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text


@router.get("", response_model=List[CategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db)) -> list:
    result = await db.execute(select(Category).order_by(Category.order.asc(), Category.name_uz.asc()))
    return list(result.scalars().all())


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> Category:
    slug = data.slug.strip() if data.slug else slugify(data.name_en or data.name_uz)

    existing = await db.execute(select(Category).where(Category.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug allaqachon mavjud")

    category = Category(
        id=uuid.uuid4(),
        name_uz=data.name_uz,
        name_ru=data.name_ru,
        name_en=data.name_en,
        slug=slug,
        order=data.order,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> Category:
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topilmadi")

    if data.slug:
        conflict = await db.execute(
            select(Category).where(Category.slug == data.slug, Category.id != category_id)
        )
        if conflict.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug allaqachon mavjud")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    await db.flush()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topilmadi")
    await db.delete(category)
