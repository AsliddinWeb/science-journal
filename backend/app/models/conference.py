import uuid
from datetime import datetime, date
from enum import Enum as PyEnum
from sqlalchemy import (
    String, Text, Boolean, DateTime, Date, Enum, Integer,
    ForeignKey, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.article import ArticleLanguage


class ConferencePaperStatus(str, PyEnum):
    draft = "draft"
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"
    published = "published"


class Conference(Base):
    __tablename__ = "conferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    description: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    organizer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

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
    sessions: Mapped[list["ConferenceSession"]] = relationship(
        "ConferenceSession", back_populates="conference", cascade="all, delete-orphan",
        order_by="ConferenceSession.order"
    )
    papers: Mapped[list["ConferencePaper"]] = relationship(
        "ConferencePaper", back_populates="conference"
    )

    def __repr__(self) -> str:
        return f"<Conference {self.id}>"


class ConferenceSession(Base):
    __tablename__ = "conference_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conference_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conferences.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    description: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    conference: Mapped["Conference"] = relationship("Conference", back_populates="sessions")
    papers: Mapped[list["ConferencePaper"]] = relationship(
        "ConferencePaper", back_populates="session"
    )

    def __repr__(self) -> str:
        return f"<ConferenceSession {self.id}>"


class ConferencePaper(Base):
    __tablename__ = "conference_papers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    abstract: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    keywords: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    language: Mapped[ArticleLanguage] = mapped_column(
        Enum(ArticleLanguage, create_constraint=False, native_enum=False),
        nullable=False, default=ArticleLanguage.uz
    )

    conference_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conferences.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conference_sessions.id"), nullable=True, index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    doi: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    pdf_file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    pdf_file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    pages: Mapped[str | None] = mapped_column(String(50), nullable=True)

    status: Mapped[ConferencePaperStatus] = mapped_column(
        Enum(ConferencePaperStatus, name="conferencespaperstatus", create_constraint=False),
        nullable=False, default=ConferencePaperStatus.draft, index=True
    )
    published_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    references: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    funding: Mapped[str | None] = mapped_column(Text, nullable=True)

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
        "User", foreign_keys=[author_id]
    )
    conference: Mapped["Conference"] = relationship("Conference", back_populates="papers")
    session: Mapped["ConferenceSession | None"] = relationship("ConferenceSession", back_populates="papers")
    co_authors: Mapped[list["ConferencePaperAuthor"]] = relationship(
        "ConferencePaperAuthor", back_populates="paper", cascade="all, delete-orphan",
        order_by="ConferencePaperAuthor.order"
    )

    def __repr__(self) -> str:
        return f"<ConferencePaper {self.id}>"


class ConferencePaperAuthor(Base):
    __tablename__ = "conference_paper_authors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conference_papers.id", ondelete="CASCADE"), nullable=False, index=True
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
    paper: Mapped["ConferencePaper"] = relationship("ConferencePaper", back_populates="co_authors")
    user: Mapped["User | None"] = relationship("User")

    def __repr__(self) -> str:
        return f"<ConferencePaperAuthor paper={self.paper_id} order={self.order}>"
