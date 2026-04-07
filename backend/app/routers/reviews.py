from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone
from app.database import get_db
from app.models.review import Review, ReviewStatus
from app.models.article import Article, ArticleStatus
from app.models.user import User
from app.schemas.review import (
    ReviewAssign, ReviewDecline, ReviewSubmit,
    ReviewSummaryOut, ReviewOut,
)
from app.dependencies import require_editor, require_reviewer, get_current_user
import uuid

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


def _load_review_with_relations():
    return (
        selectinload(Review.reviewer),
        selectinload(Review.article),
    )


# ─── Editor: pending assignment ───────────────────────────────────────────────

@router.get("/pending-assignment", response_model=List[dict])
async def get_pending_assignment(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_editor),
) -> list:
    """Articles submitted/under_review that need reviewer assignment."""
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.author), selectinload(Article.reviews))
        .where(Article.status.in_([ArticleStatus.submitted, ArticleStatus.under_review]))
        .order_by(Article.submission_date.asc().nulls_last())
    )
    articles = result.scalars().all()
    out = []
    for a in articles:
        active_reviews = [r for r in a.reviews if r.status != ReviewStatus.declined]
        out.append({
            "id": str(a.id),
            "title": a.title,
            "language": a.language,
            "status": a.status.value,
            "submission_date": a.submission_date.isoformat() if a.submission_date else None,
            "author": {
                "id": str(a.author.id),
                "full_name": a.author.full_name,
                "email": a.author.email,
            } if a.author else None,
            "review_count": len(active_reviews),
            "category_id": str(a.category_id) if a.category_id else None,
        })
    return out


# ─── Editor: assign reviewer ─────────────────────────────────────────────────

@router.post("/{article_id}/assign", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def assign_reviewer(
    article_id: uuid.UUID,
    data: ReviewAssign,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_editor),
) -> Review:
    """Assign a reviewer to an article (up to 3 per article)."""
    article_result = await db.execute(select(Article).where(Article.id == article_id))
    article = article_result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Check reviewer exists and has reviewer role
    reviewer_result = await db.execute(select(User).where(User.id == data.reviewer_id))
    reviewer = reviewer_result.scalar_one_or_none()
    if not reviewer:
        raise HTTPException(status_code=404, detail="Reviewer not found")

    # Limit: max 3 active reviewers
    existing_count = await db.execute(
        select(func.count(Review.id))
        .where(Review.article_id == article_id)
        .where(Review.status != ReviewStatus.declined)
    )
    if existing_count.scalar_one() >= 3:
        raise HTTPException(status_code=400, detail="Maximum 3 reviewers per article")

    # Prevent duplicate assignment
    dup = await db.execute(
        select(Review)
        .where(Review.article_id == article_id)
        .where(Review.reviewer_id == data.reviewer_id)
        .where(Review.status != ReviewStatus.declined)
    )
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Reviewer already assigned to this article")

    now = datetime.now(timezone.utc)
    review = Review(
        id=uuid.uuid4(),
        article_id=article_id,
        reviewer_id=data.reviewer_id,
        status=ReviewStatus.pending,
        deadline=data.deadline,
        editor_comments=data.editor_comments,
        invitation_sent_at=now,
    )
    db.add(review)

    if article.status == ArticleStatus.submitted:
        article.status = ArticleStatus.under_review

    await db.flush()

    # Fire email task
    try:
        from app.tasks.email_tasks import send_reviewer_invitation_task
        send_reviewer_invitation_task.delay(
            str(review.id),
            reviewer.email,
            reviewer.full_name,
            article.title.get("en") or article.title.get("ru") or article.title.get("uz") or "Untitled",
        )
    except Exception:
        pass

    result = await db.execute(
        select(Review)
        .options(*_load_review_with_relations())
        .where(Review.id == review.id)
    )
    return result.scalar_one()


# ─── Editor: all reviews ──────────────────────────────────────────────────────

@router.get("/all", response_model=List[ReviewOut])
async def get_all_reviews(
    article_id: Optional[uuid.UUID] = Query(None),
    reviewer_id: Optional[uuid.UUID] = Query(None),
    review_status: Optional[ReviewStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_editor),
) -> list:
    """Editor: list all reviews with optional filters."""
    query = (
        select(Review)
        .options(*_load_review_with_relations())
        .order_by(Review.created_at.desc())
    )
    if article_id:
        query = query.where(Review.article_id == article_id)
    if reviewer_id:
        query = query.where(Review.reviewer_id == reviewer_id)
    if review_status:
        query = query.where(Review.status == review_status)

    result = await db.execute(query)
    return result.scalars().all()


# ─── Reviewer: my reviews ─────────────────────────────────────────────────────

@router.get("/my", response_model=List[ReviewSummaryOut])
async def get_my_reviews(
    current_user: User = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db),
) -> list:
    """Reviewer: get all reviews assigned to me."""
    result = await db.execute(
        select(Review)
        .options(*_load_review_with_relations())
        .where(Review.reviewer_id == current_user.id)
        .order_by(Review.created_at.desc())
    )
    return result.scalars().all()


# ─── Reviewer: review detail ──────────────────────────────────────────────────

@router.get("/{review_id}", response_model=ReviewOut)
async def get_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Review:
    """Get a single review. Reviewer sees own review; editor sees all."""
    result = await db.execute(
        select(Review)
        .options(*_load_review_with_relations())
        .where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    is_editor = current_user.role.value in ("superadmin", "editor")
    if not is_editor and review.reviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return review


# ─── Reviewer: accept invitation ─────────────────────────────────────────────

@router.post("/{review_id}/accept", response_model=ReviewSummaryOut)
async def accept_review(
    review_id: uuid.UUID,
    current_user: User = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db),
) -> Review:
    """Reviewer accepts the invitation."""
    result = await db.execute(
        select(Review)
        .options(*_load_review_with_relations())
        .where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.reviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your review")
    if review.status != ReviewStatus.pending:
        raise HTTPException(status_code=409, detail="Invitation already responded to")

    review.status = ReviewStatus.accepted
    review.accepted_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(review)
    return review


# ─── Reviewer: decline invitation ────────────────────────────────────────────

@router.post("/{review_id}/decline", response_model=ReviewSummaryOut)
async def decline_review(
    review_id: uuid.UUID,
    data: ReviewDecline,
    current_user: User = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db),
) -> Review:
    """Reviewer declines the invitation."""
    result = await db.execute(
        select(Review)
        .options(*_load_review_with_relations())
        .where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.reviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your review")
    if review.status not in (ReviewStatus.pending, ReviewStatus.accepted):
        raise HTTPException(status_code=409, detail="Cannot decline in current status")

    review.status = ReviewStatus.declined
    review.decline_reason = data.reason
    review.declined_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(review)
    return review


# ─── Reviewer: submit review ──────────────────────────────────────────────────

@router.post("/{review_id}/submit", response_model=ReviewSummaryOut)
async def submit_review(
    review_id: uuid.UUID,
    data: ReviewSubmit,
    current_user: User = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db),
) -> Review:
    """Reviewer submits completed review."""
    result = await db.execute(
        select(Review)
        .options(*_load_review_with_relations())
        .where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.reviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your review")
    if review.status == ReviewStatus.completed:
        raise HTTPException(status_code=409, detail="Review already submitted")
    if review.status == ReviewStatus.declined:
        raise HTTPException(status_code=409, detail="Cannot submit a declined review")

    review.status = ReviewStatus.completed
    review.recommendation = data.recommendation
    review.comments_to_author = data.comments_to_author
    review.comments_to_editor = data.comments_to_editor
    review.submitted_at = datetime.now(timezone.utc)

    await db.flush()

    # Notify editor
    try:
        from app.tasks.email_tasks import send_editor_new_review_task
        send_editor_new_review_task.delay(str(review_id))
    except Exception:
        pass

    await db.refresh(review)
    return review
