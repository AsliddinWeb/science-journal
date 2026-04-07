import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ReviewStatus(str, PyEnum):
    pending = "pending"
    accepted = "accepted"
    completed = "completed"
    declined = "declined"


class ReviewRecommendation(str, PyEnum):
    accept = "accept"
    minor_revision = "minor_revision"
    major_revision = "major_revision"
    reject = "reject"


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus), nullable=False, default=ReviewStatus.pending
    )
    recommendation: Mapped[ReviewRecommendation | None] = mapped_column(
        Enum(ReviewRecommendation), nullable=True
    )
    comments_to_author: Mapped[str | None] = mapped_column(Text, nullable=True)
    comments_to_editor: Mapped[str | None] = mapped_column(Text, nullable=True)
    editor_comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    decline_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    invitation_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    declined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    article: Mapped["Article"] = relationship("Article", back_populates="reviews")
    reviewer: Mapped["User"] = relationship("User", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review article={self.article_id} reviewer={self.reviewer_id}>"
