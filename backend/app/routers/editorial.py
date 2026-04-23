from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.editorial import EditorialBoardMember, EditorialRole
from app.dependencies import require_editor
from pydantic import BaseModel, ConfigDict
from uuid import UUID
import uuid as _uuid
from datetime import datetime

router = APIRouter(prefix="/api/editorial", tags=["editorial"])


class EditorialMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: Optional[UUID] = None
    name: str
    title: Optional[str] = None
    affiliation: Optional[str] = None
    country: Optional[str] = None
    role: EditorialRole
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    orcid_id: Optional[str] = None
    email: Optional[str] = None
    degree: Optional[str] = None
    specialization: Optional[str] = None
    scopus_id: Optional[str] = None
    researcher_id: Optional[str] = None
    google_scholar_url: Optional[str] = None
    website_url: Optional[str] = None
    order: int
    is_active: bool
    created_at: datetime


class EditorialMemberCreate(BaseModel):
    name: str
    title: Optional[str] = None
    affiliation: Optional[str] = None
    country: Optional[str] = None
    role: EditorialRole = EditorialRole.reviewer
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    orcid_id: Optional[str] = None
    email: Optional[str] = None
    degree: Optional[str] = None
    specialization: Optional[str] = None
    scopus_id: Optional[str] = None
    researcher_id: Optional[str] = None
    google_scholar_url: Optional[str] = None
    website_url: Optional[str] = None
    is_active: bool = True
    order: int = 0
    user_id: Optional[UUID] = None


class ReorderRequest(BaseModel):
    ordered_ids: List[UUID]


@router.get("/board", response_model=List[EditorialMemberRead])
async def get_editorial_board(db: AsyncSession = Depends(get_db)) -> list:
    """Public: get all active editorial board members ordered."""
    result = await db.execute(
        select(EditorialBoardMember)
        .where(EditorialBoardMember.is_active == True)
        .order_by(EditorialBoardMember.order)
    )
    return result.scalars().all()


@router.get("/members", response_model=List[EditorialMemberRead])
async def list_members(
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> list:
    """Admin: list all editorial board members (including inactive)."""
    result = await db.execute(
        select(EditorialBoardMember).order_by(EditorialBoardMember.order)
    )
    return result.scalars().all()


@router.post("/board", response_model=EditorialMemberRead, status_code=status.HTTP_201_CREATED)
async def create_board_member_legacy(
    data: EditorialMemberCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> EditorialBoardMember:
    """Legacy endpoint kept for backwards compatibility."""
    member = EditorialBoardMember(id=_uuid.uuid4(), **data.model_dump())
    db.add(member)
    await db.flush()
    await db.refresh(member)
    return member


@router.post("/members", response_model=EditorialMemberRead, status_code=status.HTTP_201_CREATED)
async def create_member(
    data: EditorialMemberCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> EditorialBoardMember:
    """Admin: add a new editorial board member."""
    member = EditorialBoardMember(id=_uuid.uuid4(), **data.model_dump())
    db.add(member)
    await db.flush()
    await db.refresh(member)
    return member


@router.put("/members/{member_id}", response_model=EditorialMemberRead)
async def update_member(
    member_id: UUID,
    data: EditorialMemberCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> EditorialBoardMember:
    """Admin: update an editorial board member."""
    result = await db.execute(
        select(EditorialBoardMember).where(EditorialBoardMember.id == member_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    for k, v in data.model_dump().items():
        setattr(member, k, v)
    await db.flush()
    await db.refresh(member)
    return member


@router.delete("/board/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board_member(
    member_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> None:
    """Legacy delete endpoint."""
    result = await db.execute(
        select(EditorialBoardMember).where(EditorialBoardMember.id == member_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    await db.delete(member)


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> None:
    """Admin: remove an editorial board member."""
    result = await db.execute(
        select(EditorialBoardMember).where(EditorialBoardMember.id == member_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    await db.delete(member)


@router.patch("/members/reorder", status_code=status.HTTP_200_OK)
async def reorder_members(
    data: ReorderRequest,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Admin: reorder editorial board members by supplying ordered list of IDs."""
    for idx, member_id in enumerate(data.ordered_ids):
        result = await db.execute(
            select(EditorialBoardMember).where(EditorialBoardMember.id == member_id)
        )
        member = result.scalar_one_or_none()
        if member:
            member.order = idx
    await db.flush()
    return {"ok": True}
