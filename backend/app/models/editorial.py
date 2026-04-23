import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Text, Integer, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class EditorialRole(str, PyEnum):
    editor_in_chief = "editor_in_chief"
    associate_editor = "associate_editor"
    section_editor = "section_editor"
    reviewer = "reviewer"


class EditorialBoardMember(Base):
    __tablename__ = "editorial_board_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    affiliation: Mapped[str | None] = mapped_column(String(500), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[EditorialRole] = mapped_column(
        Enum(EditorialRole), nullable=False, default=EditorialRole.reviewer
    )
    photo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    orcid_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Additional profile fields
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    degree: Mapped[str | None] = mapped_column(String(100), nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(500), nullable=True)
    scopus_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    researcher_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    google_scholar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<EditorialBoardMember {self.name}>"
