from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.models.article import Article, ArticleStatus, ArticleAuthor
from app.models.user import User, UserRole
from app.schemas.article import ArticleRead, ArticleStatusUpdate, AdminArticleCreate, AdminArticleUpdate
from app.schemas.user import UserRead, AdminUserUpdate
from app.schemas.common import PaginatedResponse
from app.dependencies import require_admin, require_editor
from app.utils.pagination import PaginationParams, paginate_response
from app.services.export import export_articles_csv
from pydantic import BaseModel
import uuid
import io

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ─── Stats ────────────────────────────────────────────────────────────────────

@router.get("/stats/overview")
async def admin_stats_overview(
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Dashboard stats overview."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_articles = (
        await db.execute(select(func.count()).select_from(Article))
    ).scalar_one()

    published_this_month = (
        await db.execute(
            select(func.count()).select_from(Article).where(
                Article.status == ArticleStatus.published,
                Article.published_date >= month_start,
            )
        )
    ).scalar_one()

    registered_users = (
        await db.execute(select(func.count()).select_from(User))
    ).scalar_one()

    total_downloads = (
        await db.execute(
            select(func.coalesce(func.sum(Article.download_count), 0)).select_from(Article)
        )
    ).scalar_one()

    pending_submissions = (
        await db.execute(
            select(func.count()).select_from(Article).where(
                Article.status == ArticleStatus.submitted
            )
        )
    ).scalar_one()

    under_review = (
        await db.execute(
            select(func.count()).select_from(Article).where(
                Article.status == ArticleStatus.under_review
            )
        )
    ).scalar_one()

    awaiting_decision = (
        await db.execute(
            select(func.count()).select_from(Article).where(
                Article.status == ArticleStatus.accepted,
                Article.volume_id == None,
            )
        )
    ).scalar_one()

    # Last month comparison for total_articles
    last_month_start = (month_start - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_articles = (
        await db.execute(
            select(func.count()).select_from(Article).where(
                Article.status == ArticleStatus.published,
                Article.published_date >= last_month_start,
                Article.published_date < month_start,
            )
        )
    ).scalar_one()

    change_pct = 0
    if last_month_articles > 0:
        change_pct = round(((published_this_month - last_month_articles) / last_month_articles) * 100)

    return {
        "total_articles": total_articles,
        "published_this_month": published_this_month,
        "registered_users": registered_users,
        "total_downloads": int(total_downloads),
        "pending_submissions": pending_submissions,
        "under_review": under_review,
        "awaiting_decision": awaiting_decision,
        "published_change_pct": change_pct,
    }


@router.get("/stats/monthly")
async def admin_stats_monthly(
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Monthly publications for last 12 months (for chart)."""
    now = datetime.now(timezone.utc)
    labels = []
    data = []

    for i in range(11, -1, -1):
        # Calculate month start/end
        month = now.month - i
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        month_start = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            month_end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            month_end = datetime(year, month + 1, 1, tzinfo=timezone.utc)

        count = (
            await db.execute(
                select(func.count()).select_from(Article).where(
                    Article.status == ArticleStatus.published,
                    Article.published_date >= month_start,
                    Article.published_date < month_end,
                )
            )
        ).scalar_one()

        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        labels.append(f"{month_names[month - 1]} {year}")
        data.append(count)

    return {"labels": labels, "data": data}


@router.get("/stats/top-downloads")
async def admin_stats_top_downloads(
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> list:
    """Top 5 most downloaded articles."""
    result = await db.execute(
        select(Article)
        .where(Article.status == ArticleStatus.published)
        .order_by(Article.download_count.desc())
        .limit(5)
    )
    articles = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "title": a.title,
            "download_count": a.download_count,
        }
        for a in articles
    ]


@router.get("/stats/recent-submissions")
async def admin_recent_submissions(
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> list:
    """Last 10 submitted/under_review articles."""
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.author))
        .where(Article.status.in_([
            ArticleStatus.submitted,
            ArticleStatus.under_review,
            ArticleStatus.revision_required,
        ]))
        .order_by(Article.created_at.desc())
        .limit(10)
    )
    articles = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "title": a.title,
            "author": a.author.full_name if a.author else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "status": a.status.value,
        }
        for a in articles
    ]


# ─── Articles ─────────────────────────────────────────────────────────────────

@router.get("/articles", response_model=PaginatedResponse[ArticleRead])
async def admin_list_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[ArticleStatus] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    volume_id: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Admin: list all articles with optional filtering."""
    params = PaginationParams(page=page, limit=limit)

    query = select(Article).options(
        selectinload(Article.author),
        selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
        selectinload(Article.volume),
        selectinload(Article.issue),
    )

    if status_filter:
        query = query.where(Article.status == status_filter)
    if search:
        from sqlalchemy import cast, String
        term = f"%{search}%"
        query = query.where(
            or_(
                Article.title.cast(String).ilike(term),
            )
        )
    if category_id:
        try:
            query = query.where(Article.category_id == uuid.UUID(category_id))
        except ValueError:
            pass
    if volume_id:
        try:
            query = query.where(Article.volume_id == uuid.UUID(volume_id))
        except ValueError:
            pass
    if language:
        query = query.where(Article.language == language)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Article.created_at.desc()).offset(params.offset).limit(params.limit)
    result = await db.execute(query)
    articles = result.scalars().all()

    return paginate_response(articles, total, params.page, params.limit)


@router.get("/articles/export")
async def export_articles(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    volume_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> StreamingResponse:
    """Export filtered articles to CSV."""
    # Build query with filters
    query = select(Article).options(
        selectinload(Article.author),
        selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
        selectinload(Article.volume),
        selectinload(Article.issue),
        selectinload(Article.category),
    )
    if status_filter:
        try:
            query = query.where(Article.status == ArticleStatus(status_filter))
        except ValueError:
            pass
    if search:
        from sqlalchemy import cast, String
        term = f"%{search}%"
        query = query.where(Article.title.cast(String).ilike(term))
    if category_id:
        try:
            query = query.where(Article.category_id == uuid.UUID(category_id))
        except ValueError:
            pass
    if volume_id:
        try:
            query = query.where(Article.volume_id == uuid.UUID(volume_id))
        except ValueError:
            pass

    query = query.order_by(Article.created_at.desc())
    result = await db.execute(query)
    articles = result.scalars().all()

    csv_bytes = export_articles_csv(articles)
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=articles_export.csv"},
    )


@router.post("/articles", response_model=ArticleRead, status_code=status.HTTP_201_CREATED)
async def admin_create_article(
    data: AdminArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_editor),
) -> Article:
    """Admin: create article on behalf of any registered user."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    submission_date = now if data.status == ArticleStatus.submitted else None
    published_date = data.published_date or (now if data.status == ArticleStatus.published else None)

    article = Article(
        id=uuid.uuid4(),
        title=data.title,
        abstract=data.abstract,
        keywords=data.keywords,
        language=data.language,
        category_id=data.category_id,
        volume_id=data.volume_id,
        issue_id=data.issue_id,
        author_id=data.author_id,
        status=data.status,
        doi=data.doi,
        pdf_file_path=data.pdf_file_path,
        pdf_file_size=data.pdf_file_size,
        cover_image_url=data.cover_image_url,
        cover_letter=data.cover_letter,
        article_type=data.article_type,
        pages=data.pages,
        references=data.references,
        funding=data.funding,
        conflict_of_interest=data.conflict_of_interest,
        acknowledgments=data.acknowledgments,
        submission_date=submission_date,
        published_date=published_date,
    )
    db.add(article)
    await db.flush()

    for i, author_data in enumerate(data.co_authors):
        co_author = ArticleAuthor(
            id=uuid.uuid4(),
            article_id=article.id,
            user_id=author_data.user_id,
            guest_name=author_data.guest_name,
            guest_email=author_data.guest_email,
            guest_affiliation=author_data.guest_affiliation,
            guest_orcid=author_data.guest_orcid,
            order=author_data.order if author_data.order else i + 1,
            is_corresponding=author_data.is_corresponding,
        )
        db.add(co_author)

    await db.flush()
    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
            selectinload(Article.volume),
            selectinload(Article.issue),
        )
        .where(Article.id == article.id)
    )
    return result.scalar_one()


@router.put("/articles/{article_id}", response_model=ArticleRead)
async def admin_update_article(
    article_id: uuid.UUID,
    data: AdminArticleUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> Article:
    """Admin: update any field of any article."""
    from datetime import datetime, timezone

    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
            selectinload(Article.volume),
            selectinload(Article.issue),
        )
        .where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    update_data = data.model_dump(exclude_unset=True)

    # Auto-set dates when status changes
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == ArticleStatus.published and not article.published_date:
            article.published_date = datetime.now(timezone.utc)
        if new_status == ArticleStatus.submitted and not article.submission_date:
            article.submission_date = datetime.now(timezone.utc)

    # Replace co_authors if provided (delete old, add new)
    co_authors_payload = update_data.pop("co_authors", None)

    for field, value in update_data.items():
        setattr(article, field, value)

    if co_authors_payload is not None:
        for existing in list(article.co_authors):
            await db.delete(existing)
        await db.flush()
        for i, ca in enumerate(co_authors_payload):
            db.add(ArticleAuthor(
                id=uuid.uuid4(),
                article_id=article.id,
                user_id=ca.get("user_id"),
                guest_name=ca.get("guest_name"),
                guest_email=ca.get("guest_email"),
                guest_affiliation=ca.get("guest_affiliation"),
                guest_orcid=ca.get("guest_orcid"),
                order=ca.get("order") or (i + 1),
                is_corresponding=bool(ca.get("is_corresponding")),
            ))

    await db.flush()

    # Re-fetch so co_authors + relations reflect the new state
    reload = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
            selectinload(Article.volume),
            selectinload(Article.issue),
        )
        .where(Article.id == article_id)
    )
    return reload.scalar_one()


@router.patch("/articles/{article_id}/status", response_model=ArticleRead)
async def update_article_status(
    article_id: uuid.UUID,
    data: ArticleStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> Article:
    """Update an article's workflow status."""
    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
            selectinload(Article.volume),
            selectinload(Article.issue),
        )
        .where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    article.status = data.status
    if data.status == ArticleStatus.published and not article.published_date:
        article.published_date = datetime.now(timezone.utc)
    if data.status == ArticleStatus.submitted and not article.submission_date:
        article.submission_date = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(article)
    return article


@router.patch("/articles/bulk-assign")
async def bulk_assign_articles(
    data: dict,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Assign multiple articles to an issue."""
    article_ids = data.get("article_ids", [])
    issue_id = data.get("issue_id")

    if not issue_id or not article_ids:
        raise HTTPException(status_code=400, detail="article_ids and issue_id required")

    try:
        issue_uuid = uuid.UUID(issue_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid issue_id")

    # Find volume_id for the issue
    from app.models.volume import Issue as IssueModel
    issue_result = await db.execute(select(IssueModel).where(IssueModel.id == issue_uuid))
    issue = issue_result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    updated = 0
    for aid in article_ids:
        try:
            a_uuid = uuid.UUID(aid)
        except ValueError:
            continue
        a_result = await db.execute(select(Article).where(Article.id == a_uuid))
        article = a_result.scalar_one_or_none()
        if article:
            article.issue_id = issue_uuid
            article.volume_id = issue.volume_id
            updated += 1

    await db.flush()
    return {"updated": updated}


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_admin),
) -> None:
    """Admin: delete an article."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    await db.delete(article)


@router.post("/articles/{article_id}/doi", response_model=ArticleRead)
async def assign_doi(
    article_id: uuid.UUID,
    doi: str,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> Article:
    """Assign a DOI to a published article."""
    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
            selectinload(Article.volume),
            selectinload(Article.issue),
        )
        .where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    existing = await db.execute(select(Article).where(Article.doi == doi, Article.id != article_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="DOI already in use")

    article.doi = doi
    await db.flush()
    await db.refresh(article)
    return article


# ─── Users ────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=PaginatedResponse[UserRead])
async def admin_list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    country: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_editor),
) -> dict:
    """Admin/Editor: list users with filters."""
    params = PaginationParams(page=page, limit=limit)
    query = select(User)
    if role:
        query = query.where(User.role == role)
    if search:
        term = f"%{search}%"
        query = query.where(
            or_(User.full_name.ilike(term), User.email.ilike(term))
        )
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if country:
        query = query.where(User.country == country)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(User.created_at.desc()).offset(params.offset).limit(params.limit)
    result = await db.execute(query)
    users = result.scalars().all()

    return paginate_response(users, total, params.page, params.limit)


@router.patch("/users/{user_id}", response_model=UserRead)
async def admin_update_user(
    user_id: uuid.UUID,
    data: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_admin),
) -> User:
    """Admin: update any profile field of any user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)

    # Guard unique email
    new_email = update_data.get("email")
    if new_email and new_email != user.email:
        existing = await db.execute(select(User).where(User.email == new_email, User.id != user_id))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: uuid.UUID,
    role: UserRole,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_admin),
) -> dict:
    """Admin: change a user's role."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.role = role
    await db.flush()
    return {"id": str(user.id), "role": user.role.value}


@router.patch("/users/{user_id}/active")
async def toggle_user_active(
    user_id: uuid.UUID,
    active: bool,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_admin),
) -> dict:
    """Admin: activate or deactivate a user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = active
    await db.flush()
    return {"id": str(user.id), "is_active": user.is_active}


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_admin),
) -> None:
    """Admin: delete a user account."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)


class InviteReviewerRequest(BaseModel):
    email: str
    full_name: Optional[str] = None


@router.post("/users/invite-reviewer")
async def invite_reviewer(
    data: InviteReviewerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_editor),
) -> dict:
    """Admin: invite a user as reviewer by email."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user:
        # Upgrade existing user to reviewer if they're a reader/author
        if user.role in [UserRole.reader, UserRole.author]:
            user.role = UserRole.reviewer
            await db.flush()
        return {"status": "existing", "user_id": str(user.id), "email": user.email}

    # Create a new inactive user with reviewer role and send invitation
    from app.services.email import send_email
    import secrets
    invite_token = secrets.token_urlsafe(32)

    new_user = User(
        id=uuid.uuid4(),
        email=data.email,
        full_name=data.full_name or data.email.split("@")[0],
        password_hash="INVITE_PENDING",
        role=UserRole.reviewer,
        is_active=False,
        is_verified=False,
    )
    db.add(new_user)
    await db.flush()

    # Send invitation email (best-effort)
    try:
        await send_email(
            to_email=data.email,
            subject="Reviewer Invitation — Scientific Journal",
            body=f"""You have been invited to join as a reviewer.\n\nPlease register at /register?invite={invite_token}&email={data.email}\n""",
        )
    except Exception:
        pass

    return {"status": "invited", "user_id": str(new_user.id), "email": new_user.email}
