import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    String, Text, Boolean, DateTime, Enum, Integer,
    ForeignKey, func, Index
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ArticleStatus(str, PyEnum):
    draft = "draft"
    submitted = "submitted"
    under_review = "under_review"
    revision_required = "revision_required"
    accepted = "accepted"
    rejected = "rejected"
    published = "published"


class ArticleLanguage(str, PyEnum):
    uz = "uz"
    ru = "ru"
    en = "en"


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Multilingual title (JSONB: {"uz": "...", "ru": "...", "en": "..."})
    title: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    abstract: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    keywords: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    doi: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    submission_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus), nullable=False, default=ArticleStatus.draft, index=True
    )
    language: Mapped[ArticleLanguage] = mapped_column(
        Enum(ArticleLanguage), nullable=False, default=ArticleLanguage.uz
    )

    volume_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("volumes.id"), nullable=True, index=True
    )
    issue_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issues.id"), nullable=True, index=True
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    pdf_file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    pdf_file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Pages (e.g. "82-86")
    pages: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Extended fields
    article_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)
    references: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    funding: Mapped[str | None] = mapped_column(Text, nullable=True)
    conflict_of_interest: Mapped[str | None] = mapped_column(Text, nullable=True)
    acknowledgments: Mapped[str | None] = mapped_column(Text, nullable=True)

    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Full-text search vector (updated via trigger or app code)
    search_vector: Mapped[str | None] = mapped_column(
        "search_vector", Text, nullable=True
    )

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
    author: Mapped["User"] = relationship(
        "User", back_populates="articles", foreign_keys=[author_id]
    )
    volume: Mapped["Volume | None"] = relationship("Volume", back_populates="articles")
    issue: Mapped["Issue | None"] = relationship("Issue", back_populates="articles")
    category: Mapped["Category | None"] = relationship("Category", back_populates="articles")
    co_authors: Mapped[list["ArticleAuthor"]] = relationship(
        "ArticleAuthor", back_populates="article", cascade="all, delete-orphan",
        order_by="ArticleAuthor.order"
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="article", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_articles_status_published", "status", "published_date"),
        Index("ix_articles_volume_issue", "volume_id", "issue_id"),
    )

    def __repr__(self) -> str:
        return f"<Article {self.id}>"


class ArticleAuthor(Base):
    __tablename__ = "article_authors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    # For guest/external authors not registered in the system
    guest_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    guest_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    guest_affiliation: Mapped[str | None] = mapped_column(String(500), nullable=True)
    guest_orcid: Mapped[str | None] = mapped_column(String(50), nullable=True)

    order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_corresponding: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    article: Mapped["Article"] = relationship("Article", back_populates="co_authors")
    user: Mapped["User | None"] = relationship("User", back_populates="article_authorships")

    def __repr__(self) -> str:
        return f"<ArticleAuthor article={self.article_id} order={self.order}>"
