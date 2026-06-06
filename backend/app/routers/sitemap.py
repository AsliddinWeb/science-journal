from fastapi import APIRouter
from fastapi.responses import Response, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.article import Article, ArticleStatus
from app.models.volume import Volume, Issue
from app.models.home_settings import HomeSettings
from app.config import settings
from app.services.cache import get_cached, set_cached
from fastapi import Depends
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sitemap"])

SITE_URL = settings.APP_URL
# "/" is intentionally omitted — it is a 302 redirect to /{journal_slug}/index.
# Paths mirror the OJS URL convention so harvesters (Google Scholar etc.)
# recognise the site's structure.
STATIC_PATHS = [
    ("/index", "1.0", "daily"),
    ("/issue/current", "0.9", "weekly"),
    ("/issue/archive", "0.8", "weekly"),
    ("/search", "0.6", "monthly"),
    ("/about", "0.6", "monthly"),
    ("/about/editorialTeam", "0.6", "monthly"),
    ("/about/contact", "0.5", "monthly"),
    ("/about/submissions", "0.7", "monthly"),
    ("/about/editorialPolicies", "0.5", "monthly"),
    ("/about/privacy", "0.4", "monthly"),
    # Legacy non-OJS paths kept so existing inbound links still appear in the
    # sitemap until search engines fully migrate to the canonical OJS forms.
    ("/articles", "0.7", "daily"),
    ("/archive", "0.6", "weekly"),
    ("/editorial-board", "0.5", "monthly"),
    ("/contact", "0.4", "monthly"),
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
            select(Article.public_id, Article.updated_at)
            .where(Article.status == ArticleStatus.published)
            .order_by(Article.published_date.desc())
        )
        articles = articles_result.all()

        issues_result = await db.execute(
            select(Issue.public_id, Issue.published_date)
            .order_by(Issue.published_date.desc().nulls_last())
        )
        issues = issues_result.all()

        # Resolve the journal_slug from home_settings — the actual home URL
        hs_result = await db.execute(
            select(HomeSettings.journal_slug).where(HomeSettings.id == "default")
        )
        journal_slug = hs_result.scalar_one_or_none() or "academic-book-journal"

        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
        ]

        # All static, issue and article URLs live under /{journal_slug}/...
        for path, priority, freq in STATIC_PATHS:
            lines.append(_url_entry(f"{SITE_URL}/{journal_slug}{path}", changefreq=freq, priority=priority))

        # Issue pages — OJS-canonical `/issue/view/{public_id}` form.
        for public_id, published_date in issues:
            loc = f"{SITE_URL}/{journal_slug}/issue/view/{public_id}"
            lastmod = published_date.isoformat() if published_date else None
            lines.append(_url_entry(loc, lastmod=lastmod, changefreq="monthly", priority="0.7"))

        # Article pages — OJS-canonical `/article/view/{public_id}` form.
        for public_id, updated_at in articles:
            loc = f"{SITE_URL}/{journal_slug}/article/view/{public_id}"
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
async def robots(db: AsyncSession = Depends(get_db)) -> PlainTextResponse:
    hs_result = await db.execute(
        select(HomeSettings.journal_slug).where(HomeSettings.id == "default")
    )
    journal_slug = hs_result.scalar_one_or_none() or "academic-book-journal"
    # `Allow:` is listed BEFORE the broader `Disallow: /api/` so crawlers
    # following the longest-match rule (Google, Bing, Scholar) keep access
    # to article PDFs at /api/uploads/... — without this Scholar reads
    # citation_pdf_url but the path is robots-blocked, so it can't extract
    # full text.
    content = f"""User-agent: *
Allow: /
Allow: /api/uploads/
Disallow: /admin
Disallow: /api/
Disallow: /author
Disallow: /reviewer

Sitemap: {SITE_URL}/sitemap.xml

# OAI-PMH harvesting endpoint (Scholar, DOAJ, Crossref)
# Identify: {SITE_URL}/{journal_slug}/oai?verb=Identify
"""
    return PlainTextResponse(content=content)
