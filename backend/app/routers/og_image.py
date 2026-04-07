from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.article import Article, ArticleStatus, ArticleAuthor
from app.models.user import User
from app.services.cache import get_cached, set_cached
import uuid
import logging
import io

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/og-image", tags=["og-image"])

BG_COLOR = (30, 58, 95)       # #1E3A5F
TITLE_COLOR = (255, 255, 255)
AUTHOR_COLOR = (180, 200, 220)
BADGE_BG = (255, 255, 255, 40)
ACCENT_COLOR = (99, 179, 237)  # light blue
IMG_W, IMG_H = 1200, 630


def _wrap_text(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = f"{current} {word}".strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _generate_og_image(title: str, authors: str, volume_info: str) -> bytes:
    from PIL import Image, ImageDraw, ImageFont
    import os

    img = Image.new("RGB", (IMG_W, IMG_H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Gradient overlay — subtle lighter top strip
    for y in range(200):
        alpha = int(20 * (1 - y / 200))
        for x in range(IMG_W):
            r, g, b = img.getpixel((x, y))
            img.putpixel((x, y), (min(r + alpha, 255), min(g + alpha, 255), min(b + alpha, 255)))

    # Decorative circles
    draw.ellipse([-80, -80, 200, 200], fill=(255, 255, 255, 0), outline=(255, 255, 255, 15), width=2)
    draw.ellipse([1000, 450, 1350, 800], fill=(255, 255, 255, 0), outline=(255, 255, 255, 10), width=2)

    try:
        font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        if not os.path.exists(font_path_bold):
            font_path_bold = font_path_bold.replace("truetype/dejavu/", "")
        title_font = ImageFont.truetype(font_path_bold, 52) if os.path.exists(font_path_bold) else ImageFont.load_default()
        author_font = ImageFont.truetype(font_path, 30) if os.path.exists(font_path.replace("-Bold", "")) else ImageFont.load_default()
        logo_font = ImageFont.truetype(font_path_bold, 22) if os.path.exists(font_path_bold) else ImageFont.load_default()
        badge_font = ImageFont.truetype(font_path, 20) if os.path.exists(font_path.replace("-Bold", "")) else ImageFont.load_default()
    except Exception:
        title_font = author_font = logo_font = badge_font = ImageFont.load_default()

    # Logo area top-left
    draw.text((60, 50), "⬡ Science and Innovation", font=logo_font, fill=ACCENT_COLOR)
    draw.text((60, 80), "ISSN 2181-3337 · scientists.uz", font=badge_font, fill=(150, 180, 210))

    # Horizontal divider
    draw.line([(60, 115), (1140, 115)], fill=(255, 255, 255, 30), width=1)

    # Title — wrapped
    title_lines = _wrap_text(title, 38)[:4]
    y = 160
    for line in title_lines:
        draw.text((60, y), line, font=title_font, fill=TITLE_COLOR)
        y += 68

    # Authors
    if authors:
        draw.text((60, y + 20), authors[:80], font=author_font, fill=AUTHOR_COLOR)
        y += 60

    # Bottom bar
    draw.rectangle([(0, IMG_H - 70), (IMG_W, IMG_H)], fill=(15, 40, 72))
    if volume_info:
        draw.text((60, IMG_H - 48), volume_info, font=badge_font, fill=ACCENT_COLOR)
    draw.text((IMG_W - 300, IMG_H - 48), "Open Access · CC BY 4.0", font=badge_font, fill=(150, 180, 210))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


@router.get("/{article_id}")
async def og_image(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    cache_key = f"og:{article_id}"
    cached_hex = await get_cached(cache_key)
    if cached_hex:
        return Response(
            content=bytes.fromhex(cached_hex),
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
        )
        .where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article or article.status != ArticleStatus.published:
        raise HTTPException(status_code=404, detail="Article not found")

    title = (article.title or {}).get("en") or (article.title or {}).get("uz") or "Untitled"

    author_names: list[str] = []
    if article.author:
        author_names.append(article.author.full_name)
    for ca in (article.co_authors or []):
        name = ca.user.full_name if ca.user else ca.guest_name
        if name:
            author_names.append(name)
    authors_str = ", ".join(author_names[:3])
    if len(author_names) > 3:
        authors_str += f" +{len(author_names) - 3}"

    volume_info = ""
    if article.volume_id:
        volume_info = f"Vol. {article.volume_id}"

    try:
        png_bytes = _generate_og_image(title, authors_str, volume_info)
        await set_cached(cache_key, png_bytes.hex(), ttl=86400)
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=86400"},
        )
    except Exception as exc:
        logger.warning("OG image generation failed for %s: %s", article_id, exc)
        raise HTTPException(status_code=500, detail="Image generation failed")
