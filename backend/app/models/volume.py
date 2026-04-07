import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, Boolean, DateTime, Integer, Date, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Volume(Base):
    __tablename__ = "volumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    issues: Mapped[list["Issue"]] = relationship(
        "Issue", back_populates="volume", cascade="all, delete-orphan",
        order_by="Issue.number"
    )
    articles: Mapped[list["Article"]] = relationship("Article", back_populates="volume")

    def __repr__(self) -> str:
        return f"<Volume {self.number} ({self.year})>"


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    volume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("volumes.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    published_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    volume: Mapped["Volume"] = relationship("Volume", back_populates="issues")
    articles: Mapped[list["Article"]] = relationship("Article", back_populates="issue")

    def __repr__(self) -> str:
        return f"<Issue {self.number} vol={self.volume_id}>"
