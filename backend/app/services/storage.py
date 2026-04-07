"""Local disk storage service. Files are saved to /app/uploads/ inside the container."""
import asyncio
from pathlib import Path

_UPLOADS_ROOT = Path(__file__).resolve().parents[2] / "uploads"


async def upload_file(content: bytes, s3_key: str, content_type: str = "application/octet-stream") -> str:
    """Save bytes to local disk. Returns the key (relative path)."""
    dest = _UPLOADS_ROOT / s3_key
    dest.parent.mkdir(parents=True, exist_ok=True)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, dest.write_bytes, content)
    return s3_key


async def get_file_url(s3_key: str) -> str:
    """Return the URL to serve this file."""
    if s3_key.startswith("/api/uploads/"):
        return s3_key
    return f"/api/uploads/{s3_key}"


async def delete_file(s3_key: str) -> None:
    """Delete a file from local disk."""
    path = _UPLOADS_ROOT / s3_key
    if path.exists():
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, path.unlink)
