from fastapi import APIRouter
from fastapi.responses import Response, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.article import Article, ArticleStatus
from app.models.volume import Volume, Issue
from app.config import settings
from app.services.cache import get_cached, set_cached
from fastapi import Depends
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sitemap"])

SITE_URL = settings.APP_URL
STATIC_PATHS = [
    ("/", "1.0", "daily"),
    ("/articles", "0.9", "daily"),
    ("/archive", "0.8", "weekly"),
    ("/editorial-board", "0.6", "monthly"),
    ("/contact", "0.5", "monthly"),
    ("/pages/about", "0.6", "monthly"),
    ("/pages/aims-scope", "0.6", "monthly"),
    ("/pages/open-access", "0.5", "monthly"),
    ("/pages/peer-review", "0.5", "monthly"),
    ("/pages/author-guidelines", "0.7", "monthly"),
    ("/pages/indexing", "0.5", "monthly"),
]
LANGS = ["uz", "ru", "en"]


def _url_entry(loc: str, lastmod: str | None = None, changefreq: str = "monthly", priority: str = "0.5") -> str:
    lines = [f"  <url>", f"    <loc>{loc}</loc>"]
    if lastmod:
        lines.append(f"    <lastmod>{lastmod[:10]}</lastmod>")
    lines.append(f"    <changefreq>{changefreq}</changefreq>")
    lines.append(f"    <priority>{priority}</priority>")
    for lang in LANGS:
        lang_url = f"{SITE_URL}/{lang}{loc.replace(SITE_URL, '')}"
        lines.append(f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{lang_url}"/>')
    lines.append(f"    <xhtml:link rel=\"alternate\" hreflang=\"x-default\" href=\"{loc}\"/>")
    lines.append(f"  </url>")
    return "\n".join(lines)


@router.api_route("/sitemap.xml", methods=["GET", "HEAD"], include_in_schema=False)
async def sitemap(db: AsyncSession = Depends(get_db)) -> Response:
    cached = await get_cached("sitemap")
    if cached:
        return Response(content=cached, media_type="application/xml")

    try:
        articles_result = await db.execute(
            select(Article.id, Article.updated_at)
            .where(Article.status == ArticleStatus.published)
            .order_by(Article.published_date.desc())
        )
        articles = articles_result.all()

        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
        ]

        for path, priority, freq in STATIC_PATHS:
            lines.append(_url_entry(f"{SITE_URL}{path}", changefreq=freq, priority=priority))

        for article_id, updated_at in articles:
            loc = f"{SITE_URL}/articles/{article_id}"
            lastmod = updated_at.isoformat() if updated_at else None
            lines.append(_url_entry(loc, lastmod=lastmod, changefreq="monthly", priority="0.8"))

        lines.append("</urlset>")
        xml = "\n".join(lines)

        await set_cached("sitemap", xml, ttl=3600)
        return Response(content=xml, media_type="application/xml")
    except Exception as exc:
        logger.error("Sitemap generation failed: %s", exc)
        return Response(content='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>', media_type="application/xml")


@router.api_route("/robots.txt", methods=["GET", "HEAD"], include_in_schema=False)
async def robots() -> PlainTextResponse:
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/
Disallow: /author
Disallow: /reviewer

Sitemap: {SITE_URL}/sitemap.xml
"""
    return PlainTextResponse(content=content)
