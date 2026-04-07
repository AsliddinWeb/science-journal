from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
from app.models.article import ArticleStatus, ArticleLanguage
from app.schemas.user import UserReadPublic


class ArticleAuthorCreate(BaseModel):
    user_id: Optional[UUID] = None
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_affiliation: Optional[str] = None
    guest_orcid: Optional[str] = None
    order: int = 1
    is_corresponding: bool = False


class ArticleAuthorRead(BaseModel):
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


class MultilingualField(BaseModel):
    uz: str = ""
    ru: str = ""
    en: str = ""


class ArticleCreate(BaseModel):
    title: dict  # {"uz": "...", "ru": "...", "en": "..."}
    abstract: dict
    keywords: List[str] = []
    language: ArticleLanguage = ArticleLanguage.uz
    category_id: Optional[UUID] = None
    co_authors: List[ArticleAuthorCreate] = []
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    cover_image_url: Optional[str] = None
    cover_letter: Optional[str] = None
    article_type: Optional[str] = None
    references: Optional[List[str]] = None
    funding: Optional[str] = None
    conflict_of_interest: Optional[str] = None
    acknowledgments: Optional[str] = None

    @field_validator("title", "abstract")
    @classmethod
    def validate_multilingual(cls, v: dict) -> dict:
        if not any(v.get(lang) for lang in ("uz", "ru", "en")):
            raise ValueError("At least one language version must be provided")
        return v


class ArticleUpdate(BaseModel):
    title: Optional[dict] = None
    abstract: Optional[dict] = None
    keywords: Optional[List[str]] = None
    language: Optional[ArticleLanguage] = None
    category_id: Optional[UUID] = None
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    cover_image_url: Optional[str] = None
    cover_letter: Optional[str] = None
    article_type: Optional[str] = None
    references: Optional[List[str]] = None
    funding: Optional[str] = None
    conflict_of_interest: Optional[str] = None
    acknowledgments: Optional[str] = None


class AdminArticleCreate(BaseModel):
    """Admin can create article on behalf of any user and set any field."""
    title: dict
    abstract: dict
    keywords: List[str] = []
    language: ArticleLanguage = ArticleLanguage.uz
    category_id: Optional[UUID] = None
    volume_id: Optional[UUID] = None
    issue_id: Optional[UUID] = None
    author_id: UUID
    co_authors: List[ArticleAuthorCreate] = []
    status: ArticleStatus = ArticleStatus.draft
    doi: Optional[str] = None
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    cover_image_url: Optional[str] = None
    cover_letter: Optional[str] = None
    article_type: Optional[str] = None
    references: Optional[List[str]] = None
    funding: Optional[str] = None
    conflict_of_interest: Optional[str] = None
    acknowledgments: Optional[str] = None

    @field_validator("title", "abstract")
    @classmethod
    def validate_multilingual(cls, v: dict) -> dict:
        if not any(v.get(lang) for lang in ("uz", "ru", "en")):
            raise ValueError("At least one language version must be provided")
        return v


class AdminArticleUpdate(BaseModel):
    """Admin can update any field of any article."""
    title: Optional[dict] = None
    abstract: Optional[dict] = None
    keywords: Optional[List[str]] = None
    language: Optional[ArticleLanguage] = None
    category_id: Optional[UUID] = None
    volume_id: Optional[UUID] = None
    issue_id: Optional[UUID] = None
    author_id: Optional[UUID] = None
    status: Optional[ArticleStatus] = None
    doi: Optional[str] = None
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    cover_image_url: Optional[str] = None
    cover_letter: Optional[str] = None
    article_type: Optional[str] = None
    references: Optional[List[str]] = None
    funding: Optional[str] = None
    conflict_of_interest: Optional[str] = None
    acknowledgments: Optional[str] = None


class ArticleRevisionCreate(BaseModel):
    pdf_file_path: str
    pdf_file_size: Optional[int] = None
    cover_letter: Optional[str] = None


class ArticleStatusUpdate(BaseModel):
    status: ArticleStatus
    reason: Optional[str] = None


class ReviewForAuthor(BaseModel):
    """Review data visible to the author — no confidential editor comments."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recommendation: Optional[str] = None
    comments_to_author: Optional[str] = None
    submitted_at: Optional[datetime] = None


class ArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: dict
    abstract: dict
    keywords: List[Any]
    doi: Optional[str] = None
    submission_date: Optional[datetime] = None
    published_date: Optional[datetime] = None
    status: ArticleStatus
    language: ArticleLanguage
    volume_id: Optional[UUID] = None
    issue_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    author_id: UUID
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    cover_image_url: Optional[str] = None
    article_type: Optional[str] = None
    cover_letter: Optional[str] = None
    references: Optional[List[Any]] = None
    funding: Optional[str] = None
    conflict_of_interest: Optional[str] = None
    acknowledgments: Optional[str] = None
    download_count: int
    view_count: int
    created_at: datetime
    updated_at: datetime
    author: Optional[UserReadPublic] = None
    co_authors: List[ArticleAuthorRead] = []


class ArticleStatusDetail(ArticleRead):
    """Extended article read with author-visible review comments."""
    reviews_for_author: List[ReviewForAuthor] = []


class ArticleListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: dict
    abstract: dict
    keywords: List[Any]
    doi: Optional[str] = None
    published_date: Optional[datetime] = None
    submission_date: Optional[datetime] = None
    status: ArticleStatus
    language: ArticleLanguage
    volume_id: Optional[UUID] = None
    issue_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    cover_image_url: Optional[str] = None
    download_count: int
    view_count: int
    created_at: datetime
    updated_at: datetime
    author: Optional[UserReadPublic] = None
    co_authors: List[ArticleAuthorRead] = []
