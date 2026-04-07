from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.review import ReviewStatus, ReviewRecommendation


class ReviewerInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    full_name: str
    email: str
    affiliation: Optional[str] = None
    avatar_url: Optional[str] = None


class ArticleBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: dict
    language: str


# ─── Input schemas ────────────────────────────────────────────────────────────

class ReviewAssign(BaseModel):
    reviewer_id: UUID
    deadline: Optional[datetime] = None
    editor_comments: Optional[str] = None


class ReviewDecline(BaseModel):
    reason: Optional[str] = None


class ReviewSubmit(BaseModel):
    recommendation: ReviewRecommendation
    comments_to_author: str
    comments_to_editor: Optional[str] = None

    @field_validator("comments_to_author")
    @classmethod
    def validate_comments(cls, v: str) -> str:
        if len(v.strip()) < 50:
            raise ValueError("Comments to author must be at least 50 characters")
        return v


class ArticleDecision(BaseModel):
    decision: str  # accept | reject | minor_revision | major_revision
    comments_to_author: Optional[str] = None


# ─── Output schemas ───────────────────────────────────────────────────────────

class ReviewSummaryOut(BaseModel):
    """Lightweight review — for reviewer's own list."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    article_id: UUID
    reviewer_id: UUID
    status: ReviewStatus
    recommendation: Optional[ReviewRecommendation] = None
    deadline: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    reviewer: Optional[ReviewerInfo] = None
    article: Optional[ArticleBrief] = None


class ReviewOut(ReviewSummaryOut):
    """Full detail — for editors (includes confidential fields)."""
    comments_to_author: Optional[str] = None
    comments_to_editor: Optional[str] = None
    editor_comments: Optional[str] = None
    decline_reason: Optional[str] = None
    invitation_sent_at: Optional[datetime] = None
    declined_at: Optional[datetime] = None


# ─── Legacy aliases (keep backward compat with old router) ───────────────────
ReviewCreate = ReviewAssign
ReviewRead = ReviewSummaryOut
ReviewReadFull = ReviewOut
