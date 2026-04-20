from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.dependencies import require_author, require_editor, get_current_user
from app.models.user import User
from app.services.storage import upload_file, get_file_url
import uuid

router = APIRouter(prefix="/api/upload", tags=["upload"])

MAX_PDF_SIZE = 20 * 1024 * 1024    # 20 MB
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_VIDEO_SIZE = 200 * 1024 * 1024  # 200 MB


@router.post("/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(require_author),
) -> dict:
    if file.content_type not in ("application/pdf",):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only PDF files are allowed")

    content = await file.read()
    if len(content) > MAX_PDF_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File size exceeds 20 MB")

    s3_key = f"articles/pdf/{uuid.uuid4()}.pdf"
    await upload_file(content, s3_key, content_type="application/pdf")
    url = await get_file_url(s3_key)

    return {"s3_key": s3_key, "url": url, "file_size": len(content), "filename": file.filename}


@router.post("/avatar")
async def upload_avatar_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict:
    allowed_types = ("image/jpeg", "image/png", "image/webp")
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only JPEG, PNG or WebP images are allowed")

    content = await file.read()
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Avatar file size exceeds 5 MB")

    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "jpg"
    s3_key = f"avatars/{uuid.uuid4()}.{ext}"
    await upload_file(content, s3_key, content_type=file.content_type or "image/jpeg")
    url = await get_file_url(s3_key)

    return {"s3_key": s3_key, "url": url, "file_size": len(content), "filename": file.filename}


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(require_author),
) -> dict:
    allowed_types = ("image/jpeg", "image/png", "image/webp")
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only JPEG, PNG or WebP images are allowed",
        )

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image file size exceeds 10 MB",
        )

    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "jpg"
    s3_key = f"images/{uuid.uuid4()}.{ext}"
    await upload_file(content, s3_key, content_type=file.content_type or "image/jpeg")
    url = await get_file_url(s3_key)

    return {"s3_key": s3_key, "url": url, "file_size": len(content), "filename": file.filename}


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    _: User = Depends(require_editor),
) -> dict:
    """Admin/editor: upload an MP4/WebM video for the home hero."""
    allowed_types = ("video/mp4", "video/webm", "video/ogg", "video/quicktime")
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only MP4, WebM, OGG or MOV videos are allowed",
        )

    content = await file.read()
    if len(content) > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Video file size exceeds 200 MB",
        )

    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "mp4"
    s3_key = f"videos/{uuid.uuid4()}.{ext}"
    await upload_file(content, s3_key, content_type=file.content_type or "video/mp4")
    url = await get_file_url(s3_key)

    return {"s3_key": s3_key, "url": url, "file_size": len(content), "filename": file.filename}
