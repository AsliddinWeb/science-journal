"""
Read-only endpoint for fetching an issue by its UUID alone — used by the
OJS-style URL `/{slug}/issue/view/{issueId}`, which (unlike the legacy
`/archive/{volumeId}/issues/{issueId}` route) does not carry the volume id.

Write operations on issues stay under /api/volumes/{volume_id}/issues/...
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.article import Article, ArticleStatus
from app.models.volume import Issue, Volume

router = APIRouter(prefix="/api/issues", tags=["issues"])


@router.get("/{issue_id}")
async def get_issue(issue_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    issue = (
        await db.execute(
            select(Issue)
            .options(selectinload(Issue.volume))
            .where(Issue.id == issue_id)
        )
    ).scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    article_count = (
        await db.execute(
            select(func.count())
            .select_from(Article)
            .where(Article.issue_id == issue.id, Article.status == ArticleStatus.published)
        )
    ).scalar_one()

    volume = issue.volume
    return {
        "id": issue.id,
        "volume_id": issue.volume_id,
        "number": issue.number,
        "published_date": issue.published_date,
        "cover_image_url": issue.cover_image_url,
        "description": issue.description,
        "full_pdf_url": issue.full_pdf_url,
        "created_at": issue.created_at,
        "article_count": article_count,
        "volume": {
            "id": volume.id,
            "number": volume.number,
            "year": volume.year,
            "is_current": volume.is_current,
            "description": volume.description,
            "cover_image_url": volume.cover_image_url,
            "created_at": volume.created_at,
        } if volume else None,
    }
