from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime, timezone
from app.database import get_db
from app.models.conference import (
    Conference, ConferenceSession, ConferencePaper,
    ConferencePaperAuthor, ConferencePaperStatus,
)
from app.models.user import User
from app.schemas.conference import (
    ConferenceCreate, ConferenceUpdate, ConferenceRead,
    ConferenceSessionCreate, ConferenceSessionUpdate, ConferenceSessionRead,
    AdminConferencePaperCreate, AdminConferencePaperUpdate,
    ConferencePaperRead, ConferencePaperListItem,
)
from app.schemas.common import PaginatedResponse
from app.dependencies import require_admin, require_editor
from app.utils.pagination import PaginationParams, paginate_response
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/api/admin/conferences", tags=["admin-conferences"])


# ─── Conferences ──────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse[ConferenceRead])
async def admin_list_conferences(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Admin: list all conferences with optional filtering."""
    params = PaginationParams(page=page, limit=limit)

    query = select(Conference).options(selectinload(Conference.sessions))

    if search:
        from sqlalchemy import cast, String
        term = f"%{search}%"
        query = query.where(
            or_(
                Conference.title.cast(String).ilike(term),
                Conference.description.cast(String).ilike(term),
            )
        )
    if year:
        query = query.where(Conference.year == year)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Conference.start_date.desc()).offset(params.offset).limit(params.limit)
    result = await db.execute(query)
    conferences = result.scalars().all()

    return paginate_response(conferences, total, params.page, params.limit)


@router.post("", response_model=ConferenceRead, status_code=status.HTTP_201_CREATED)
async def admin_create_conference(
    data: ConferenceCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Admin: create a new conference."""
    conference = Conference(
        id=uuid.uuid4(),
        title=data.title,
        description=data.description,
        year=data.year,
        start_date=data.start_date,
        end_date=data.end_date,
        location=data.location,
        is_active=data.is_active if data.is_active is not None else True,
        cover_image_url=data.cover_image_url,
    )
    db.add(conference)
    await db.flush()

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
        "created_at": conference.created_at,
        "sessions": [],
    }


@router.put("/{conference_id}", response_model=ConferenceRead)
async def admin_update_conference(
    conference_id: uuid.UUID,
    data: ConferenceUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Admin: update an existing conference."""
    result = await db.execute(
        select(Conference)
        .options(selectinload(Conference.sessions))
        .where(Conference.id == conference_id)
    )
    conference = result.scalar_one_or_none()
    if not conference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(conference, field, value)

    await db.flush()

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
        sessions_with_counts.append({
            "id": session.id,
            "conference_id": session.conference_id,
            "title": session.title,
            "description": session.description,
            "order": session.order,
            "created_at": session.created_at,
            "paper_count": count_result.scalar_one(),
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
        "created_at": conference.created_at,
        "sessions": sessions_with_counts,
    }


@router.delete("/{conference_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_conference(
    conference_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_admin),
) -> None:
    """Admin: delete a conference (requires admin role)."""
    result = await db.execute(
        select(Conference).where(Conference.id == conference_id)
    )
    conference = result.scalar_one_or_none()
    if not conference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    await db.delete(conference)


# ─── Sessions ─────────────────────────────────────────────────────────────────

@router.post("/{conference_id}/sessions", response_model=ConferenceSessionRead, status_code=status.HTTP_201_CREATED)
async def admin_create_session(
    conference_id: uuid.UUID,
    data: ConferenceSessionCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Admin: create a new session under a conference."""
    result = await db.execute(
        select(Conference).where(Conference.id == conference_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")

    session = ConferenceSession(
        id=uuid.uuid4(),
        conference_id=conference_id,
        title=data.title,
        description=data.description,
        order=data.order if data.order is not None else 0,
    )
    db.add(session)
    await db.flush()

    return {
        "id": session.id,
        "conference_id": session.conference_id,
        "title": session.title,
        "description": session.description,
        "order": session.order,
        "created_at": session.created_at,
        "paper_count": 0,
    }


@router.put("/{conference_id}/sessions/{session_id}", response_model=ConferenceSessionRead)
async def admin_update_session(
    conference_id: uuid.UUID,
    session_id: uuid.UUID,
    data: ConferenceSessionUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Admin: update a conference session."""
    result = await db.execute(
        select(ConferenceSession).where(
            ConferenceSession.id == session_id,
            ConferenceSession.conference_id == conference_id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(session, field, value)

    await db.flush()

    count_result = await db.execute(
        select(func.count())
        .select_from(ConferencePaper)
        .where(
            ConferencePaper.session_id == session.id,
            ConferencePaper.status == ConferencePaperStatus.published,
        )
    )

    return {
        "id": session.id,
        "conference_id": session.conference_id,
        "title": session.title,
        "description": session.description,
        "order": session.order,
        "created_at": session.created_at,
        "paper_count": count_result.scalar_one(),
    }


@router.delete("/{conference_id}/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_session(
    conference_id: uuid.UUID,
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> None:
    """Admin: delete a conference session."""
    result = await db.execute(
        select(ConferenceSession).where(
            ConferenceSession.id == session_id,
            ConferenceSession.conference_id == conference_id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    await db.delete(session)


# ─── Papers ───────────────────────────────────────────────────────────────────

@router.get("/{conference_id}/papers", response_model=PaginatedResponse[ConferencePaperListItem])
async def admin_list_papers(
    conference_id: uuid.UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[ConferencePaperStatus] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    session_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Admin: list all papers for a conference (all statuses)."""
    params = PaginationParams(page=page, limit=limit)

    query = (
        select(ConferencePaper)
        .options(
            selectinload(ConferencePaper.authors),
            selectinload(ConferencePaper.session),
        )
        .where(ConferencePaper.conference_id == conference_id)
    )

    if status_filter:
        query = query.where(ConferencePaper.status == status_filter)
    if session_id:
        query = query.where(ConferencePaper.session_id == session_id)
    if search:
        from sqlalchemy import cast, String
        term = f"%{search}%"
        query = query.where(
            or_(
                ConferencePaper.title.cast(String).ilike(term),
                ConferencePaper.abstract.cast(String).ilike(term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(ConferencePaper.created_at.desc()).offset(params.offset).limit(params.limit)
    result = await db.execute(query)
    papers = result.scalars().all()

    return paginate_response(papers, total, params.page, params.limit)


@router.post("/{conference_id}/papers", response_model=ConferencePaperRead, status_code=status.HTTP_201_CREATED)
async def admin_create_paper(
    conference_id: uuid.UUID,
    data: AdminConferencePaperCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_editor),
) -> ConferencePaper:
    """Admin: create a conference paper."""
    # Verify conference exists
    conf_result = await db.execute(
        select(Conference).where(Conference.id == conference_id)
    )
    if not conf_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")

    # Verify session exists if provided
    if data.session_id:
        session_result = await db.execute(
            select(ConferenceSession).where(
                ConferenceSession.id == data.session_id,
                ConferenceSession.conference_id == conference_id,
            )
        )
        if not session_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    now = datetime.now(timezone.utc)
    published_date = now if data.status == ConferencePaperStatus.published else None

    paper = ConferencePaper(
        id=uuid.uuid4(),
        conference_id=conference_id,
        session_id=data.session_id,
        title=data.title,
        abstract=data.abstract,
        keywords=data.keywords,
        language=data.language,
        author_id=data.author_id,
        status=data.status,
        doi=data.doi,
        pdf_file_path=data.pdf_file_path,
        pdf_file_size=data.pdf_file_size,
        published_date=published_date,
    )
    db.add(paper)
    await db.flush()

    # Add authors
    if data.authors:
        for i, author_data in enumerate(data.authors):
            author = ConferencePaperAuthor(
                id=uuid.uuid4(),
                paper_id=paper.id,
                full_name=author_data.full_name,
                email=author_data.email,
                affiliation=author_data.affiliation,
                orcid=author_data.orcid,
                order=author_data.order if author_data.order else i + 1,
                is_corresponding=author_data.is_corresponding,
            )
            db.add(author)

    await db.flush()
    result = await db.execute(
        select(ConferencePaper)
        .options(
            selectinload(ConferencePaper.authors),
            selectinload(ConferencePaper.session),
        )
        .where(ConferencePaper.id == paper.id)
    )
    return result.scalar_one()


@router.put("/{conference_id}/papers/{paper_id}", response_model=ConferencePaperRead)
async def admin_update_paper(
    conference_id: uuid.UUID,
    paper_id: uuid.UUID,
    data: AdminConferencePaperUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> ConferencePaper:
    """Admin: update any field of a conference paper."""
    result = await db.execute(
        select(ConferencePaper)
        .options(
            selectinload(ConferencePaper.authors),
            selectinload(ConferencePaper.session),
        )
        .where(
            ConferencePaper.id == paper_id,
            ConferencePaper.conference_id == conference_id,
        )
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")

    update_data = data.model_dump(exclude_unset=True)

    # Auto-set published_date when status changes to published
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == ConferencePaperStatus.published and not paper.published_date:
            paper.published_date = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(paper, field, value)

    await db.flush()
    await db.refresh(paper)
    return paper


@router.delete("/{conference_id}/papers/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_paper(
    conference_id: uuid.UUID,
    paper_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> None:
    """Admin: delete a conference paper."""
    result = await db.execute(
        select(ConferencePaper).where(
            ConferencePaper.id == paper_id,
            ConferencePaper.conference_id == conference_id,
        )
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
    await db.delete(paper)


class ConferencePaperStatusUpdate(BaseModel):
    status: ConferencePaperStatus


@router.patch("/{conference_id}/papers/{paper_id}/status", response_model=ConferencePaperRead)
async def admin_update_paper_status(
    conference_id: uuid.UUID,
    paper_id: uuid.UUID,
    data: ConferencePaperStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> ConferencePaper:
    """Admin: change the status of a conference paper."""
    result = await db.execute(
        select(ConferencePaper)
        .options(
            selectinload(ConferencePaper.authors),
            selectinload(ConferencePaper.session),
        )
        .where(
            ConferencePaper.id == paper_id,
            ConferencePaper.conference_id == conference_id,
        )
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")

    paper.status = data.status
    if data.status == ConferencePaperStatus.published and not paper.published_date:
        paper.published_date = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(paper)
    return paper
