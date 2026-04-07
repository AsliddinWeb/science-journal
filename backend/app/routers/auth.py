from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate, UserRead, UserLogin, TokenResponse, RefreshTokenRequest
)
from app.services.auth import (
    hash_password, create_access_token, create_refresh_token,
    decode_refresh_token, authenticate_user,
    generate_verification_token, decode_verification_token,
)
from app.dependencies import get_current_user
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Register a new user. Sends a verification email."""
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email address already registered",
        )

    user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        affiliation=user_data.affiliation,
        country=user_data.country,
        orcid_id=user_data.orcid_id,
        role=UserRole.author,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = generate_verification_token(str(user.id))
    user.verification_token = token
    await db.flush()

    # Send verification email in background
    background_tasks.add_task(
        _send_verification_bg,
        user.email,
        user.full_name,
        token,
    )

    return {"message": "Registration successful. Please check your email to verify your account."}


def _send_verification_bg(email: str, name: str, token: str) -> None:
    """Synchronous wrapper for sending verification email (used in BackgroundTasks)."""
    import asyncio
    from app.services.email import send_verification_email
    try:
        asyncio.run(send_verification_email(email, name, token))
    except Exception:
        pass  # Don't crash the request if email fails


@router.get("/verify-email")
async def verify_email(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Verify email address using the token from the verification link."""
    user_id = decode_verification_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_verified:
        return {"message": "Email already verified"}

    # Check token matches what we stored
    if user.verification_token != token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already used verification token",
        )

    user.is_verified = True
    user.verification_token = None
    await db.flush()

    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Resend verification email to the current user."""
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified",
        )

    token = generate_verification_token(str(current_user.id))
    current_user.verification_token = token
    await db.flush()

    background_tasks.add_task(
        _send_verification_bg,
        current_user.email,
        current_user.full_name,
        token,
    )

    return {"message": "Verification email sent"}


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    user = await authenticate_user(credentials.email, credentials.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    access_token = create_access_token(str(user.id), user.role.value)
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Use a valid refresh token to obtain new access + refresh tokens."""
    user_id = decode_refresh_token(body.refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token = create_access_token(str(user.id), user.role.value)
    new_refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the currently authenticated user's profile."""
    return current_user
