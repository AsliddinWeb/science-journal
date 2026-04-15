from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Any
from datetime import datetime, date
from uuid import UUID
from app.models.article import ArticleLanguage
from app.models.conference import ConferencePaperStatus
from app.schemas.user import UserReadPublic


# ─── Conference ───────────────────────────────────────────────

class ConferenceCreate(BaseModel):
    title: dict
    description: Optional[dict] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    year: int
    cover_image_url: Optional[str] = None
    is_active: bool = True
    organizer: Optional[str] = None
    website_url: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_multilingual(cls, v: dict) -> dict:
        if not any(v.get(lang) for lang in ("uz", "ru", "en")):
            raise ValueError("At least one language version must be provided")
        return v


class ConferenceUpdate(BaseModel):
    title: Optional[dict] = None
    description: Optional[dict] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    year: Optional[int] = None
    cover_image_url: Optional[str] = None
    is_active: Optional[bool] = None
    organizer: Optional[str] = None
    website_url: Optional[str] = None


class ConferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: dict
    description: Optional[dict] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    year: int
    cover_image_url: Optional[str] = None
    is_active: bool
    organizer: Optional[str] = None
    website_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    sessions: List["ConferenceSessionRead"] = []


# ─── ConferenceSession ───────────────────────────────────────

class ConferenceSessionCreate(BaseModel):
    title: dict
    description: Optional[dict] = None
    order: int = 1
    date: Any = None

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> Any:
        if not v or v == "":
            return None
        if isinstance(v, str):
            from datetime import date as _date
            return _date.fromisoformat(v)
        return v

    @field_validator("title")
    @classmethod
    def validate_multilingual(cls, v: dict) -> dict:
        if not any(v.get(lang) for lang in ("uz", "ru", "en")):
            raise ValueError("At least one language version must be provided")
        return v


class ConferenceSessionUpdate(BaseModel):
    title: Optional[dict] = None
    description: Optional[dict] = None
    order: Optional[int] = None
    date: Any = None

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> Any:
        if not v or v == "":
            return None
        if isinstance(v, str):
            from datetime import date as _date
            return _date.fromisoformat(v)
        return v


class ConferenceSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conference_id: UUID
    title: dict
    description: Optional[dict] = None
    order: int
    date: Any = None
    created_at: datetime
    paper_count: int = 0


# ─── ConferencePaperAuthor ───────────────────────────────────

class ConferencePaperAuthorCreate(BaseModel):
    user_id: Optional[UUID] = None
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_affiliation: Optional[str] = None
    guest_orcid: Optional[str] = None
    order: int = 1
    is_corresponding: bool = False


class ConferencePaperAuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: Optional[UUID] = None
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_affiliation: Optional[str] = None
    guest_orcid: Optional[str] = None
    order: int
    is_corresponding: bool
    user: Optional[UserReadPublic] = None


# ─── ConferencePaper ─────────────────────────────────────────

class ConferencePaperCreate(BaseModel):
    title: dict
    abstract: dict
    keywords: List[str] = []
    language: ArticleLanguage = ArticleLanguage.uz
    conference_id: UUID
    session_id: Optional[UUID] = None
    co_authors: List[ConferencePaperAuthorCreate] = []
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    cover_image_url: Optional[str] = None
    references: Optional[List[str]] = None
    funding: Optional[str] = None

    @field_validator("title", "abstract")
    @classmethod
    def validate_multilingual(cls, v: dict) -> dict:
        if not any(v.get(lang) for lang in ("uz", "ru", "en")):
            raise ValueError("At least one language version must be provided")
        return v


class ConferencePaperUpdate(BaseModel):
    title: Optional[dict] = None
    abstract: Optional[dict] = None
    keywords: Optional[List[str]] = None
    language: Optional[ArticleLanguage] = None
    session_id: Optional[UUID] = None
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    cover_image_url: Optional[str] = None
    references: Optional[List[str]] = None
    funding: Optional[str] = None


class ConferencePaperRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: dict
    abstract: dict
    keywords: List[Any]
    language: ArticleLanguage
    conference_id: UUID
    session_id: Optional[UUID] = None
    author_id: UUID
    doi: Optional[str] = None
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    cover_image_url: Optional[str] = None
    pages: Optional[str] = None
    status: ConferencePaperStatus
    published_date: Optional[datetime] = None
    download_count: int
    view_count: int
    references: Optional[List[Any]] = None
    funding: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    author: Optional[UserReadPublic] = None
    co_authors: List[ConferencePaperAuthorRead] = []


class ConferencePaperListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: dict
    abstract: dict
    keywords: List[Any]
    language: ArticleLanguage
    conference_id: UUID
    session_id: Optional[UUID] = None
    doi: Optional[str] = None
    cover_image_url: Optional[str] = None
    pages: Optional[str] = None
    status: ConferencePaperStatus
    published_date: Optional[datetime] = None
    download_count: int
    view_count: int
    created_at: datetime
    updated_at: datetime
    author: Optional[UserReadPublic] = None
    co_authors: List[ConferencePaperAuthorRead] = []


# ─── Admin schemas ───────────────────────────────────────────

class AdminConferencePaperCreate(BaseModel):
    """Admin can create a conference paper on behalf of any user."""
    title: dict
    abstract: dict
    keywords: Any = []
    language: ArticleLanguage = ArticleLanguage.uz
    conference_id: UUID
    session_id: Optional[UUID] = None
    author_id: UUID
    co_authors: List[ConferencePaperAuthorCreate] = []
    status: ConferencePaperStatus = ConferencePaperStatus.draft
    doi: Optional[str] = None
    published_date: Optional[datetime] = None
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    cover_image_url: Optional[str] = None
    pages: Optional[str] = None
    references: Optional[List[str]] = None
    funding: Optional[str] = None

    @field_validator("title", "abstract")
    @classmethod
    def validate_multilingual(cls, v: dict) -> dict:
        if not any(v.get(lang) for lang in ("uz", "ru", "en")):
            raise ValueError("At least one language version must be provided")
        return v


class AdminConferencePaperUpdate(BaseModel):
    """Admin can update any field of any conference paper."""
    title: Optional[dict] = None
    abstract: Optional[dict] = None
    keywords: Optional[Any] = None
    language: Optional[ArticleLanguage] = None
    conference_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    author_id: Optional[UUID] = None
    status: Optional[ConferencePaperStatus] = None
    doi: Optional[str] = None
    published_date: Optional[datetime] = None
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    cover_image_url: Optional[str] = None
    pages: Optional[str] = None
    references: Optional[List[str]] = None
    funding: Optional[str] = None
    co_authors: Optional[List[ConferencePaperAuthorCreate]] = None


# Resolve forward references
ConferenceRead.model_rebuild()
