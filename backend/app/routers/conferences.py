from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, or_
from sqlalchemy.orm import selectinload
from typing import Optional
from app.database import get_db
from app.models.conference import (
    Conference, ConferenceSession, ConferencePaper,
    ConferencePaperAuthor, ConferencePaperStatus,
)
from app.schemas.conference import (
    ConferenceRead, ConferencePaperRead, ConferencePaperListItem,
)
from app.schemas.common import PaginatedResponse
from app.utils.pagination import PaginationParams, paginate_response
import uuid

router = APIRouter(prefix="/api/conferences", tags=["conferences"])


@router.get("", response_model=PaginatedResponse[ConferenceRead])
async def list_conferences(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    year: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List active conferences with optional year filter and search."""
    params = PaginationParams(page=page, limit=limit)

    query = (
        select(Conference)
        .options(selectinload(Conference.sessions))
        .where(Conference.is_active == True)
    )

    if year:
        query = query.where(Conference.year == year)
    if search:
        search_term = f"%{search}%"
        from sqlalchemy import cast, String
        query = query.where(
            or_(
                Conference.title.cast(String).ilike(search_term),
                Conference.description.cast(String).ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Conference.start_date.desc()).offset(params.offset).limit(params.limit)
    result = await db.execute(query)
    conferences = result.scalars().all()

    return paginate_response(conferences, total, params.page, params.limit)


@router.get("/{conference_id}", response_model=ConferenceRead)
async def get_conference(
    conference_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get conference detail with sessions and paper counts."""
    result = await db.execute(
        select(Conference)
        .options(selectinload(Conference.sessions))
        .where(Conference.id == conference_id)
    )
    conference = result.scalar_one_or_none()
    if not conference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")

    sessions_with_counts = []
    for session in conference.sessions:
        count_result = await db.execute(
            select(func.count())
            .select_from(ConferencePaper)
            .where(
                ConferencePaper.session_id == session.id,
                ConferencePaper.status == ConferencePaperStatus.published,
            )
        )
        paper_count = count_result.scalar_one()
        sessions_with_counts.append({
            "id": session.id,
            "conference_id": session.conference_id,
            "title": session.title,
            "description": session.description,
            "order": session.order,
            "created_at": session.created_at,
            "paper_count": paper_count,
        })

    return {
        "id": conference.id,
        "title": conference.title,
        "description": conference.description,
        "year": conference.year,
        "start_date": conference.start_date,
        "end_date": conference.end_date,
        "location": conference.location,
        "is_active": conference.is_active,
        "cover_image_url": conference.cover_image_url,
        "organizer": conference.organizer,
        "website_url": conference.website_url,
        "created_at": conference.created_at,
        "updated_at": conference.updated_at,
        "sessions": sessions_with_counts,
    }


@router.get("/{conference_id}/papers", response_model=PaginatedResponse[ConferencePaperListItem])
async def list_conference_papers(
    conference_id: uuid.UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    session_id: Optional[uuid.UUID] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List published papers for a conference, with optional session filter."""
    # Verify conference exists
    conf_result = await db.execute(
        select(Conference).where(Conference.id == conference_id)
    )
    if not conf_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")

    query = (
        select(ConferencePaper)
        .options(
            selectinload(ConferencePaper.co_authors),
            selectinload(ConferencePaper.session),
        )
        .where(
            ConferencePaper.conference_id == conference_id,
            ConferencePaper.status == ConferencePaperStatus.published,
        )
    )

    if session_id:
        query = query.where(ConferencePaper.session_id == session_id)
    if search:
        search_term = f"%{search}%"
        from sqlalchemy import cast, String
        query = query.where(
            or_(
                ConferencePaper.title.cast(String).ilike(search_term),
                ConferencePaper.abstract.cast(String).ilike(search_term),
            )
        )

    params = PaginationParams(page=page, limit=limit)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(ConferencePaper.created_at.desc()).offset(params.offset).limit(params.limit)
    result = await db.execute(query)
    papers = result.scalars().all()

    return paginate_response(papers, total, params.page, params.limit)


@router.get("/{conference_id}/papers/{paper_id}", response_model=ConferencePaperRead)
async def get_conference_paper(
    conference_id: uuid.UUID,
    paper_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ConferencePaper:
    """Get a conference paper detail and increment view count."""
    result = await db.execute(
        select(ConferencePaper)
        .options(
            selectinload(ConferencePaper.co_authors),
            selectinload(ConferencePaper.session),
        )
        .where(
            ConferencePaper.id == paper_id,
            ConferencePaper.conference_id == conference_id,
            ConferencePaper.status == ConferencePaperStatus.published,
        )
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")

    # Increment view count
    await db.execute(
        update(ConferencePaper)
        .where(ConferencePaper.id == paper_id)
        .values(view_count=ConferencePaper.view_count + 1)
    )
    await db.flush()

    return paper


@router.get("/{conference_id}/papers/{paper_id}/download")
async def download_conference_paper(
    conference_id: uuid.UUID,
    paper_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get PDF download URL for a conference paper and increment download count."""
    result = await db.execute(
        select(ConferencePaper)
        .where(
            ConferencePaper.id == paper_id,
            ConferencePaper.conference_id == conference_id,
            ConferencePaper.status == ConferencePaperStatus.published,
        )
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")

    if not paper.pdf_file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not available")

    # Increment download count
    await db.execute(
        update(ConferencePaper)
        .where(ConferencePaper.id == paper_id)
        .values(download_count=ConferencePaper.download_count + 1)
    )
    await db.flush()

    return {
        "download_url": paper.pdf_file_path,
        "filename": paper.pdf_file_path.split("/")[-1] if paper.pdf_file_path else None,
    }
