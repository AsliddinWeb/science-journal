from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from typing import Optional
from app.database import get_db
from app.models.article import Article, ArticleStatus, ArticleAuthor
from app.models.user import User
from app.schemas.article import (
    ArticleCreate, ArticleRead, ArticleListItem, ArticleUpdate,
    ArticleRevisionCreate, ArticleStatusDetail, ReviewForAuthor,
)
from app.schemas.common import PaginatedResponse
from app.schemas.review import ArticleDecision
from app.dependencies import get_current_user, get_current_user_optional, require_author, require_editor
from app.utils.pagination import PaginationParams, paginate_response
from app.services.cache import get_cached, set_cached, invalidate, invalidate_prefix
import hashlib
import json
import uuid

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("", response_model=PaginatedResponse[ArticleListItem])
async def list_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    volume_id: Optional[uuid.UUID] = Query(None),
    issue_id: Optional[uuid.UUID] = Query(None),
    lang: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List published articles with filtering and pagination."""
    params = PaginationParams(page=page, limit=limit)

    query = (
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
        )
        .where(Article.status == ArticleStatus.published)
    )

    if search:
        search_term = f"%{search}%"
        from sqlalchemy import or_, String
        query = query.where(
            or_(
                Article.title.cast(String).ilike(search_term),
                Article.abstract.cast(String).ilike(search_term),
            )
        )
    if category:
        from app.models.category import Category
        query = query.join(Article.category).where(Category.slug == category)
    if volume_id:
        query = query.where(Article.volume_id == volume_id)
    if issue_id:
        query = query.where(Article.issue_id == issue_id)
    if lang:
        query = query.where(Article.language == lang)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    if sort == "oldest":
        query = query.order_by(Article.published_date.asc())
    elif sort == "downloads":
        query = query.order_by(Article.download_count.desc())
    else:
        query = query.order_by(Article.published_date.desc())

    query = query.offset(params.offset).limit(params.limit)
    result = await db.execute(query)
    articles = result.scalars().all()

    return paginate_response(articles, total, params.page, params.limit)


@router.get("/my", response_model=PaginatedResponse[ArticleListItem])
async def my_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(require_author),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get the current author's own articles, optionally filtered by status."""
    params = PaginationParams(page=page, limit=limit)

    query = (
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
        )
        .where(Article.author_id == current_user.id)
        .order_by(Article.created_at.desc())
    )

    if status_filter:
        try:
            article_status = ArticleStatus(status_filter)
            query = query.where(Article.status == article_status)
        except ValueError:
            pass  # Ignore invalid status filter

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.offset(params.offset).limit(params.limit)
    result = await db.execute(query)
    articles = result.scalars().all()

    return paginate_response(articles, total, params.page, params.limit)


@router.get("/my/stats")
async def my_article_stats(
    current_user: User = Depends(require_author),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return article counts per status for the dashboard stats row."""
    rows = await db.execute(
        select(Article.status, func.count(Article.id))
        .where(Article.author_id == current_user.id)
        .group_by(Article.status)
    )
    counts = {row[0].value: row[1] for row in rows}
    total = sum(counts.values())
    return {
        "total": total,
        "draft": counts.get("draft", 0),
        "submitted": counts.get("submitted", 0),
        "under_review": counts.get("under_review", 0),
        "revision_required": counts.get("revision_required", 0),
        "accepted": counts.get("accepted", 0),
        "rejected": counts.get("rejected", 0),
        "published": counts.get("published", 0),
    }


@router.get("/{article_id}/status", response_model=ArticleStatusDetail)
async def get_article_status(
    article_id: uuid.UUID,
    current_user: User = Depends(require_author),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get article status + author-visible review comments for the submitting author."""
    from app.models.review import Review, ReviewStatus

    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
            selectinload(Article.reviews),
        )
        .where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    is_owner = current_user.id == article.author_id
    is_editor = current_user.role.value in ("superadmin", "editor")
    if not is_owner and not is_editor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Build author-visible reviews (only completed ones with author comments)
    reviews_for_author = [
        ReviewForAuthor(
            id=r.id,
            recommendation=r.recommendation.value if r.recommendation else None,
            comments_to_author=r.comments_to_author,
            submitted_at=r.submitted_at,
        )
        for r in article.reviews
        if r.status == ReviewStatus.completed and r.comments_to_author
    ]

    return {
        "id": article.id,
        "title": article.title,
        "abstract": article.abstract,
        "keywords": article.keywords,
        "doi": article.doi,
        "submission_date": article.submission_date,
        "published_date": article.published_date,
        "status": article.status,
        "language": article.language,
        "volume_id": article.volume_id,
        "issue_id": article.issue_id,
        "category_id": article.category_id,
        "author_id": article.author_id,
        "pdf_file_path": article.pdf_file_path,
        "pdf_file_size": article.pdf_file_size,
        "download_count": article.download_count,
        "view_count": article.view_count,
        "created_at": article.created_at,
        "updated_at": article.updated_at,
        "author": article.author,
        "co_authors": article.co_authors,
        "reviews_for_author": reviews_for_author,
    }


@router.get("/{article_id}", response_model=ArticleRead)
async def get_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Article:
    """Get a single article by ID. Increments view_count for published articles."""
    query = (
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
            selectinload(Article.reviews),
        )
        .where(Article.id == article_id)
    )
    result = await db.execute(query)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    is_owner = current_user and (
        current_user.id == article.author_id or current_user.role.value in ("superadmin", "editor")
    )
    if article.status != ArticleStatus.published and not is_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    if article.status == ArticleStatus.published:
        await db.execute(
            update(Article)
            .where(Article.id == article_id)
            .values(view_count=Article.view_count + 1)
        )
        # Invalidate cached stats when view count changes
        await invalidate("stats:overview")

    return article


@router.post("", response_model=ArticleRead, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_data: ArticleCreate,
    current_user: User = Depends(require_author),
    db: AsyncSession = Depends(get_db),
) -> Article:
    """Submit a new article. Saves as 'submitted' if PDF is provided, else 'draft'."""
    from datetime import datetime, timezone

    initial_status = ArticleStatus.submitted if article_data.pdf_file_path else ArticleStatus.draft
    now = datetime.now(timezone.utc) if initial_status == ArticleStatus.submitted else None

    article = Article(
        id=uuid.uuid4(),
        title=article_data.title,
        abstract=article_data.abstract,
        keywords=article_data.keywords,
        language=article_data.language,
        category_id=article_data.category_id,
        author_id=current_user.id,
        status=initial_status,
        pdf_file_path=article_data.pdf_file_path,
        pdf_file_size=article_data.pdf_file_size,
        submission_date=now,
    )
    db.add(article)
    await db.flush()

    for author_data in article_data.co_authors:
        co_author = ArticleAuthor(
            id=uuid.uuid4(),
            article_id=article.id,
            user_id=author_data.user_id,
            guest_name=author_data.guest_name,
            guest_email=author_data.guest_email,
            guest_affiliation=author_data.guest_affiliation,
            guest_orcid=author_data.guest_orcid,
            order=author_data.order,
            is_corresponding=author_data.is_corresponding,
        )
        db.add(co_author)

    await db.flush()

    # Send confirmation email if actually submitted
    if initial_status == ArticleStatus.submitted:
        title_str = (
            article_data.title.get("en")
            or article_data.title.get("ru")
            or article_data.title.get("uz")
            or "Untitled"
        )
        try:
            from app.tasks.email_tasks import send_submission_confirmation_task
            send_submission_confirmation_task.delay(
                current_user.email, current_user.full_name, title_str
            )
        except Exception:
            pass  # Celery not critical path

    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
        )
        .where(Article.id == article.id)
    )
    return result.scalar_one()


@router.put("/{article_id}", response_model=ArticleRead)
async def update_article(
    article_id: uuid.UUID,
    article_data: ArticleUpdate,
    current_user: User = Depends(require_author),
    db: AsyncSession = Depends(get_db),
) -> Article:
    """Update a draft or revision_required article."""
    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
        )
        .where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    is_owner = current_user.id == article.author_id
    is_editor = current_user.role.value in ("superadmin", "editor")
    if not is_owner and not is_editor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if is_owner and article.status not in (ArticleStatus.draft, ArticleStatus.revision_required):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit article in current status",
        )

    update_data = article_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(article, field, value)

    await db.flush()
    await db.refresh(article)
    return article


@router.post("/{article_id}/revision", response_model=ArticleRead)
async def submit_revision(
    article_id: uuid.UUID,
    revision_data: ArticleRevisionCreate,
    current_user: User = Depends(require_author),
    db: AsyncSession = Depends(get_db),
) -> Article:
    """Submit a revised PDF after revision_required decision."""
    from datetime import datetime, timezone

    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
        )
        .where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    if current_user.id != article.author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if article.status != ArticleStatus.revision_required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article is not in revision_required status",
        )

    article.pdf_file_path = revision_data.pdf_file_path
    if revision_data.pdf_file_size is not None:
        article.pdf_file_size = revision_data.pdf_file_size
    article.status = ArticleStatus.submitted
    article.submission_date = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(article)
    return article


@router.post("/{article_id}/view")
async def increment_view(article_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    """Increment view count for a published article."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article or article.status != ArticleStatus.published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    await db.execute(
        update(Article).where(Article.id == article_id).values(view_count=Article.view_count + 1)
    )
    return {"ok": True}


@router.get("/{article_id}/download")
async def download_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get a presigned download URL and increment download count."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article or article.status != ArticleStatus.published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    if not article.pdf_file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not available")

    await db.execute(
        update(Article)
        .where(Article.id == article_id)
        .values(download_count=Article.download_count + 1)
    )

    from app.services.storage import get_file_url
    url = await get_file_url(article.pdf_file_path)

    return {"download_url": url}


# ─── Editor: get all reviews for article ─────────────────────────────────────

@router.get("/{article_id}/reviews")
async def get_article_reviews(
    article_id: uuid.UUID,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
) -> list:
    """Editor: get all reviews for a specific article."""
    from app.models.review import Review, ReviewStatus
    from sqlalchemy.orm import selectinload as sl

    article_result = await db.execute(select(Article).where(Article.id == article_id))
    article = article_result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    reviews_result = await db.execute(
        select(Review)
        .options(sl(Review.reviewer))
        .where(Review.article_id == article_id)
        .order_by(Review.created_at.asc())
    )
    reviews = reviews_result.scalars().all()

    return [
        {
            "id": str(r.id),
            "reviewer_id": str(r.reviewer_id),
            "status": r.status.value,
            "recommendation": r.recommendation.value if r.recommendation else None,
            "comments_to_author": r.comments_to_author,
            "comments_to_editor": r.comments_to_editor,
            "editor_comments": r.editor_comments,
            "decline_reason": r.decline_reason,
            "deadline": r.deadline.isoformat() if r.deadline else None,
            "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
            "accepted_at": r.accepted_at.isoformat() if r.accepted_at else None,
            "declined_at": r.declined_at.isoformat() if r.declined_at else None,
            "invitation_sent_at": r.invitation_sent_at.isoformat() if r.invitation_sent_at else None,
            "created_at": r.created_at.isoformat(),
            "reviewer": {
                "id": str(r.reviewer.id),
                "full_name": r.reviewer.full_name,
                "email": r.reviewer.email,
                "affiliation": r.reviewer.affiliation,
                "avatar_url": r.reviewer.avatar_url,
            } if r.reviewer else None,
        }
        for r in reviews
    ]


# ─── Editor: make final decision ─────────────────────────────────────────────

@router.post("/{article_id}/decision", response_model=ArticleRead)
async def make_decision(
    article_id: uuid.UUID,
    data: ArticleDecision,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
) -> Article:
    """Editor makes final editorial decision on an article."""
    from datetime import datetime, timezone as tz

    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
        )
        .where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    decision_map = {
        "accept": ArticleStatus.accepted,
        "reject": ArticleStatus.rejected,
        "minor_revision": ArticleStatus.revision_required,
        "major_revision": ArticleStatus.revision_required,
    }
    new_status = decision_map.get(data.decision)
    if not new_status:
        raise HTTPException(status_code=400, detail=f"Invalid decision: {data.decision}")

    article.status = new_status
    if new_status == ArticleStatus.accepted and not article.published_date:
        # Don't auto-publish; editor must separately set to published + assign issue
        pass

    await db.flush()

    # Notify author
    if article.author:
        try:
            from app.tasks.email_tasks import send_author_decision_task
            title_str = (
                article.title.get("en") or article.title.get("ru") or article.title.get("uz") or "Untitled"
            )
            send_author_decision_task.delay(
                article.author.email,
                article.author.full_name,
                title_str,
                data.decision,
                data.comments_to_author or "",
            )
        except Exception:
            pass

    await db.refresh(article)
    return article
