from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


class VolumeCreate(BaseModel):
    number: int
    year: int
    is_current: bool = False
    description: Optional[str] = None
    cover_image_url: Optional[str] = None


class VolumeUpdate(BaseModel):
    number: Optional[int] = None
    year: Optional[int] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None


class IssueCreate(BaseModel):
    number: int
    published_date: Optional[date] = None
    cover_image_url: Optional[str] = None
    description: Optional[str] = None


class IssueUpdate(BaseModel):
    number: Optional[int] = None
    published_date: Optional[date] = None
    cover_image_url: Optional[str] = None
    description: Optional[str] = None


class IssueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    volume_id: UUID
    number: int
    published_date: Optional[date] = None
    cover_image_url: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    article_count: int = 0


class VolumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    number: int
    year: int
    is_current: bool
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    created_at: datetime
    issues: List[IssueRead] = []
