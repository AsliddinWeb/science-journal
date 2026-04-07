from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.indexing import IndexingDatabase
from app.dependencies import require_editor
from pydantic import BaseModel, ConfigDict
from uuid import UUID
import uuid as _uuid
from datetime import datetime

router = APIRouter(tags=["indexing"])


class IndexingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    url: str
    logo_url: Optional[str] = None
    description: Optional[str] = None
    order: int
    is_active: bool
    created_at: datetime


class IndexingCreate(BaseModel):
    name: str
    url: str
    logo_url: Optional[str] = None
    description: Optional[str] = None
    order: int = 0
    is_active: bool = True


@router.get("/api/indexing", response_model=List[IndexingRead])
async def list_indexing(db: AsyncSession = Depends(get_db)) -> list:
    """Public: list active indexing databases ordered by display order."""
    result = await db.execute(
        select(IndexingDatabase)
        .where(IndexingDatabase.is_active == True)
        .order_by(IndexingDatabase.order)
    )
    return result.scalars().all()


@router.get("/api/admin/indexing", response_model=List[IndexingRead])
async def admin_list_indexing(
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> list:
    """Admin: list all indexing databases."""
    result = await db.execute(
        select(IndexingDatabase).order_by(IndexingDatabase.order)
    )
    return result.scalars().all()


@router.post(
    "/api/admin/indexing",
    response_model=IndexingRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_indexing(
    data: IndexingCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> IndexingDatabase:
    item = IndexingDatabase(id=_uuid.uuid4(), **data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.put("/api/admin/indexing/{item_id}", response_model=IndexingRead)
async def update_indexing(
    item_id: UUID,
    data: IndexingCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> IndexingDatabase:
    result = await db.execute(
        select(IndexingDatabase).where(IndexingDatabase.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump().items():
        setattr(item, k, v)
    await db.flush()
    await db.refresh(item)
    return item


@router.delete("/api/admin/indexing/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_indexing(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> None:
    result = await db.execute(
        select(IndexingDatabase).where(IndexingDatabase.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(item)
