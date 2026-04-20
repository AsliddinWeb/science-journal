import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class HomeSettings(Base):
    """Singleton-style table: always one row with id='default'.
    Stores all customizable content for the homepage."""
    __tablename__ = "home_settings"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, default="default")

    # Hero section
    hero_title: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    hero_subtitle: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    hero_issn: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Hero optional video embed
    hero_video_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    hero_video_poster_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    hero_video_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # About section (inside hero)
    about_title: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    about_text: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    about_image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Journal info
    issn_online: Mapped[str | None] = mapped_column(String(50), nullable=True)
    issn_print: Mapped[str | None] = mapped_column(String(50), nullable=True)
    license_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Announcement banner
    announcement_uz: Mapped[str | None] = mapped_column(Text, nullable=True)
    announcement_ru: Mapped[str | None] = mapped_column(Text, nullable=True)
    announcement_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    announcement_active: Mapped[bool] = mapped_column(default=False, nullable=False)

    # CTA section
    cta_title: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    cta_subtitle: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Site theme (palette id — see frontend/src/theme/themes.ts)
    theme: Mapped[str] = mapped_column(String(50), nullable=False, default="indigo")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
