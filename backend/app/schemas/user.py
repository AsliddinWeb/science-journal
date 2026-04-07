from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole
import re


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    affiliation: Optional[str] = None
    country: Optional[str] = None
    orcid_id: Optional[str] = None


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("orcid_id")
    @classmethod
    def validate_orcid(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", v):
            raise ValueError("Invalid ORCID format. Expected: 0000-0000-0000-0000")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    affiliation: Optional[str] = None
    country: Optional[str] = None
    orcid_id: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """Profile update from author portal — subset of editable fields."""
    full_name: Optional[str] = None
    affiliation: Optional[str] = None
    country: Optional[str] = None
    orcid_id: Optional[str] = None

    @field_validator("orcid_id")
    @classmethod
    def validate_orcid(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", v):
            raise ValueError("Invalid ORCID format. Expected: 0000-0000-0000-0000")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip() if v else v


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserReadPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    affiliation: Optional[str] = None
    country: Optional[str] = None
    orcid_id: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole


class UserSearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: str
    affiliation: Optional[str] = None
    country: Optional[str] = None
    orcid_id: Optional[str] = None
    avatar_url: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
