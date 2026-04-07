from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserRead, UserProfileUpdate, UserSearchResult, PasswordChange,
)
from app.services.auth import verify_password, hash_password
from app.dependencies import get_current_user, require_author
import uuid

router = APIRouter(prefix="/api/users", tags=["users"])

MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB


@router.get("/me", response_model=UserRead)
async def get_my_profile(current_user: User = Depends(get_current_user)) -> User:
    """Return the current user's full profile."""
    return current_user


@router.put("/me", response_model=UserRead)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update the current user's profile fields."""
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    await db.flush()
    await db.refresh(current_user)
    return current_user


@router.post("/me/password")
async def change_password(
    body: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Change the current user's password."""
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    current_user.password_hash = hash_password(body.new_password)
    await db.flush()
    return {"message": "Password updated successfully"}


@router.post("/me/avatar", response_model=UserRead)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Upload a new avatar image. Returns updated user profile."""
    allowed_types = ("image/jpeg", "image/png", "image/webp")
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only JPEG, PNG or WebP images are allowed",
        )

    content = await file.read()
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Avatar file size exceeds 5MB",
        )

    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "jpg"
    s3_key = f"avatars/{uuid.uuid4()}.{ext}"

    from app.services.storage import upload_file
    await upload_file(content, s3_key, content_type=file.content_type or "image/jpeg")

    from app.services.storage import get_presigned_url
    avatar_url = await get_presigned_url(s3_key, expires=60 * 60 * 24 * 365)  # 1 year

    current_user.avatar_url = avatar_url
    await db.flush()
    await db.refresh(current_user)
    return current_user


@router.get("/search", response_model=list[UserSearchResult])
async def search_users(
    email: str = Query(..., min_length=3),
    current_user: User = Depends(require_author),
    db: AsyncSession = Depends(get_db),
) -> list[User]:
    """Search registered users by email (for co-author lookup)."""
    result = await db.execute(
        select(User)
        .where(User.email.ilike(f"%{email}%"))
        .where(User.id != current_user.id)
        .limit(10)
    )
    return list(result.scalars().all())
