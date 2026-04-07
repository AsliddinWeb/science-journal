from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List
from app.database import get_db
from app.models.volume import Volume, Issue
from app.models.article import Article, ArticleStatus
from app.schemas.volume import (
    VolumeCreate, VolumeRead, VolumeUpdate,
    IssueCreate, IssueRead, IssueUpdate
)
from app.dependencies import require_editor
import uuid

router = APIRouter(prefix="/api/volumes", tags=["volumes"])


@router.get("", response_model=List[VolumeRead])
async def list_volumes(db: AsyncSession = Depends(get_db)) -> list:
    """List all volumes with their issues."""
    result = await db.execute(
        select(Volume)
        .options(selectinload(Volume.issues))
        .order_by(Volume.year.desc(), Volume.number.desc())
    )
    volumes = result.scalars().all()

    volume_list = []
    for volume in volumes:
        vol_dict = {
            "id": volume.id,
            "number": volume.number,
            "year": volume.year,
            "is_current": volume.is_current,
            "description": volume.description,
            "created_at": volume.created_at,
            "issues": [],
        }
        for issue in volume.issues:
            count_result = await db.execute(
                select(func.count())
                .select_from(Article)
                .where(
                    Article.issue_id == issue.id,
                    Article.status == ArticleStatus.published
                )
            )
            article_count = count_result.scalar_one()
            vol_dict["issues"].append({
                "id": issue.id,
                "volume_id": issue.volume_id,
                "number": issue.number,
                "published_date": issue.published_date,
                "cover_image_url": issue.cover_image_url,
                "description": issue.description,
                "created_at": issue.created_at,
                "article_count": article_count,
            })
        volume_list.append(vol_dict)

    return volume_list


@router.get("/{volume_id}", response_model=VolumeRead)
async def get_volume(volume_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    """Get a specific volume with its issues."""
    result = await db.execute(
        select(Volume)
        .options(selectinload(Volume.issues))
        .where(Volume.id == volume_id)
    )
    volume = result.scalar_one_or_none()
    if not volume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volume not found")

    issues_with_counts = []
    for issue in volume.issues:
        count_result = await db.execute(
            select(func.count())
            .select_from(Article)
            .where(Article.issue_id == issue.id, Article.status == ArticleStatus.published)
        )
        issues_with_counts.append({
            "id": issue.id,
            "volume_id": issue.volume_id,
            "number": issue.number,
            "published_date": issue.published_date,
            "cover_image_url": issue.cover_image_url,
            "description": issue.description,
            "created_at": issue.created_at,
            "article_count": count_result.scalar_one(),
        })

    return {
        "id": volume.id,
        "number": volume.number,
        "year": volume.year,
        "is_current": volume.is_current,
        "description": volume.description,
        "created_at": volume.created_at,
        "issues": issues_with_counts,
    }


@router.post("", response_model=VolumeRead, status_code=status.HTTP_201_CREATED)
async def create_volume(
    data: VolumeCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Create a new volume."""
    if data.is_current:
        await db.execute(
            select(Volume).where(Volume.is_current == True)
        )
        # Unset all current volumes
        from sqlalchemy import update
        await db.execute(update(Volume).values(is_current=False))

    volume = Volume(
        id=uuid.uuid4(),
        number=data.number,
        year=data.year,
        is_current=data.is_current,
        description=data.description,
    )
    db.add(volume)
    await db.flush()

    return {
        "id": volume.id,
        "number": volume.number,
        "year": volume.year,
        "is_current": volume.is_current,
        "description": volume.description,
        "created_at": volume.created_at,
        "issues": [],
    }


@router.put("/{volume_id}", response_model=VolumeRead)
async def update_volume(
    volume_id: uuid.UUID,
    data: VolumeUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Update an existing volume."""
    result = await db.execute(
        select(Volume).options(selectinload(Volume.issues)).where(Volume.id == volume_id)
    )
    volume = result.scalar_one_or_none()
    if not volume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volume not found")

    if data.is_current:
        from sqlalchemy import update as sa_update
        await db.execute(sa_update(Volume).where(Volume.id != volume_id).values(is_current=False))

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(volume, field, value)

    await db.flush()

    issues_with_counts = []
    for issue in volume.issues:
        count_result = await db.execute(
            select(func.count())
            .select_from(Article)
            .where(Article.issue_id == issue.id, Article.status == ArticleStatus.published)
        )
        issues_with_counts.append({
            "id": issue.id,
            "volume_id": issue.volume_id,
            "number": issue.number,
            "published_date": issue.published_date,
            "cover_image_url": issue.cover_image_url,
            "description": issue.description,
            "created_at": issue.created_at,
            "article_count": count_result.scalar_one(),
        })

    return {
        "id": volume.id,
        "number": volume.number,
        "year": volume.year,
        "is_current": volume.is_current,
        "description": volume.description,
        "created_at": volume.created_at,
        "issues": issues_with_counts,
    }


@router.delete("/{volume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_volume(
    volume_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> None:
    """Delete a volume."""
    result = await db.execute(select(Volume).where(Volume.id == volume_id))
    volume = result.scalar_one_or_none()
    if not volume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volume not found")
    await db.delete(volume)


@router.post("/{volume_id}/issues", response_model=IssueRead, status_code=status.HTTP_201_CREATED)
async def create_issue(
    volume_id: uuid.UUID,
    data: IssueCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Create a new issue under a volume."""
    result = await db.execute(select(Volume).where(Volume.id == volume_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volume not found")

    issue = Issue(
        id=uuid.uuid4(),
        volume_id=volume_id,
        number=data.number,
        published_date=data.published_date,
        cover_image_url=data.cover_image_url,
        description=data.description,
    )
    db.add(issue)
    await db.flush()

    return {
        "id": issue.id,
        "volume_id": issue.volume_id,
        "number": issue.number,
        "published_date": issue.published_date,
        "cover_image_url": issue.cover_image_url,
        "description": issue.description,
        "created_at": issue.created_at,
        "article_count": 0,
    }
