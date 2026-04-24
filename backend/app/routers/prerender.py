"""
Server-rendered HTML for search-engine crawlers (esp. Google Scholar).

Google Scholar's crawler is conservative and historically does not run
JavaScript reliably. The main Vue SPA injects `citation_*` meta tags on
mount — invisible to crawlers fetching the raw document.

This router emits a minimal, fully-static HTML document with:
  * all `citation_*` meta tags for Scholar harvesting
  * open-graph + twitter + canonical for other crawlers
  * JSON-LD ScholarlyArticle structured data
  * a readable text body (title / authors / abstract / keywords / refs)
    so the page is useful even when rendered as-is

Nginx conditionally proxies bot user-agents here.
"""
from __future__ import annotations

import html as _html
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.article import Article, ArticleAuthor, ArticleStatus
from app.models.home_settings import HomeSettings

router = APIRouter(prefix="/prerender", tags=["prerender"])


# ─── helpers ─────────────────────────────────────────────────────────────────

def _e(value: Any) -> str:
    """HTML-escape a value; empty strings for None."""
    if value is None:
        return ""
    return _html.escape(str(value), quote=True)


def _pick(d: dict | None, lang: str = "en") -> str:
    """Pick a localized value from a multilingual JSON dict."""
    if not isinstance(d, dict):
        return ""
    return d.get(lang) or d.get("en") or d.get("uz") or d.get("ru") or ""


def _scholar_date(dt: datetime | None) -> str:
    if not dt:
        return ""
    return f"{dt.year:04d}/{dt.month:02d}/{dt.day:02d}"


def _flatten_list(value: Any) -> list[str]:
    """Accept either a list or a {uz,ru,en} dict of lists; return flat list."""
    if isinstance(value, list):
        return [str(x) for x in value if x]
    if isinstance(value, dict):
        out: list[str] = []
        for k in ("uz", "ru", "en"):
            part = value.get(k)
            if isinstance(part, list):
                out.extend(str(x) for x in part if x)
        seen: set[str] = set()
        uniq = []
        for x in out:
            if x not in seen:
                seen.add(x)
                uniq.append(x)
        return uniq
    return []


# ─── route ───────────────────────────────────────────────────────────────────

@router.api_route("/articles/{article_id}", methods=["GET", "HEAD"], include_in_schema=False)
async def prerender_article(
    article_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Static HTML view of a published article for crawlers."""
    try:
        article_uuid = __import__("uuid").UUID(article_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
            selectinload(Article.volume),
            selectinload(Article.issue),
        )
        .where(Article.id == article_uuid, Article.status == ArticleStatus.published)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    hs_row = (await db.execute(select(HomeSettings).where(HomeSettings.id == "default"))).scalar_one_or_none()
    site_name_en = ""
    site_name_uz = ""
    issn = ""
    publisher = ""
    if hs_row:
        site_name_en = _pick(hs_row.site_name, "en") or _pick(hs_row.hero_title, "en")
        site_name_uz = _pick(hs_row.site_name, "uz") or _pick(hs_row.hero_title, "uz")
        issn = hs_row.issn_online or hs_row.issn_print or ""
        publisher = site_name_en or site_name_uz

    # ── Fields ──
    lang = getattr(article.language, "value", str(article.language)) if article.language else "en"
    title = _pick(article.title, lang) or _pick(article.title, "en") or _pick(article.title, "uz") or "Untitled"
    abstract = _pick(article.abstract, lang) or _pick(article.abstract, "en") or _pick(article.abstract, "uz")

    # Authors: only real authors (skip superadmin) + co-authors (registered and guests)
    authors: list[dict[str, str]] = []
    if article.author and article.author.role.value != "superadmin":
        authors.append({
            "name": article.author.full_name or "",
            "affiliation": article.author.affiliation or "",
            "orcid": article.author.orcid_id or "",
        })
    for co in article.co_authors or []:
        name = (co.user.full_name if co.user else None) or co.guest_name or ""
        if not name:
            continue
        authors.append({
            "name": name,
            "affiliation": (co.user.affiliation if co.user else None) or co.guest_affiliation or "",
            "orcid": (co.user.orcid_id if co.user else None) or co.guest_orcid or "",
        })

    # Pages → first/last
    firstpage = lastpage = ""
    if article.pages:
        import re
        m = re.match(r"^\s*(\d+)\s*[-–—]\s*(\d+)\s*$", article.pages)
        if m:
            firstpage, lastpage = m.group(1), m.group(2)
        else:
            firstpage = article.pages.strip()

    # URLs
    base_url = str(settings.APP_URL).rstrip("/") if settings.APP_URL else f"{request.url.scheme}://{request.url.netloc}"
    abstract_html_url = f"{base_url}/articles/{article.id}"
    pdf_url = ""
    if article.pdf_file_path:
        p = article.pdf_file_path
        pdf_url = p if p.startswith(("http", "/")) else f"/api/uploads/{p}"
        if pdf_url.startswith("/"):
            pdf_url = f"{base_url}{pdf_url}"

    keywords = _flatten_list(article.keywords)
    references = _flatten_list(article.references)

    journal_title = site_name_en or publisher or "Journal"
    pub_date = _scholar_date(article.published_date or article.created_at)
    volume_num = str(article.volume.number) if article.volume else ""
    issue_num = str(article.issue.number) if article.issue else ""

    # ── Meta tags (Google Scholar citation_*) ──
    citation_meta: list[str] = []
    citation_meta.append(f'<meta name="citation_title" content="{_e(title)}">')
    for a in authors:
        citation_meta.append(f'<meta name="citation_author" content="{_e(a["name"])}">')
        if a["affiliation"]:
            citation_meta.append(f'<meta name="citation_author_institution" content="{_e(a["affiliation"])}">')
        if a["orcid"]:
            citation_meta.append(f'<meta name="citation_author_orcid" content="{_e(a["orcid"])}">')
    if pub_date:
        citation_meta.append(f'<meta name="citation_publication_date" content="{_e(pub_date)}">')
        citation_meta.append(f'<meta name="citation_online_date" content="{_e(pub_date)}">')
    if journal_title:
        citation_meta.append(f'<meta name="citation_journal_title" content="{_e(journal_title)}">')
    if issn:
        citation_meta.append(f'<meta name="citation_issn" content="{_e(issn)}">')
    if volume_num:
        citation_meta.append(f'<meta name="citation_volume" content="{_e(volume_num)}">')
    if issue_num:
        citation_meta.append(f'<meta name="citation_issue" content="{_e(issue_num)}">')
    if firstpage:
        citation_meta.append(f'<meta name="citation_firstpage" content="{_e(firstpage)}">')
    if lastpage:
        citation_meta.append(f'<meta name="citation_lastpage" content="{_e(lastpage)}">')
    if pdf_url:
        citation_meta.append(f'<meta name="citation_pdf_url" content="{_e(pdf_url)}">')
    if article.doi:
        citation_meta.append(f'<meta name="citation_doi" content="{_e(article.doi)}">')
    citation_meta.append(f'<meta name="citation_abstract_html_url" content="{_e(abstract_html_url)}">')
    if lang:
        citation_meta.append(f'<meta name="citation_language" content="{_e(lang)}">')
    if keywords:
        citation_meta.append(f'<meta name="citation_keywords" content="{_e("; ".join(keywords))}">')
    if publisher:
        citation_meta.append(f'<meta name="citation_publisher" content="{_e(publisher)}">')

    # Open Graph
    og_meta = [
        '<meta property="og:type" content="article">',
        f'<meta property="og:title" content="{_e(title)}">',
        f'<meta property="og:description" content="{_e(abstract[:200])}">',
        f'<meta property="og:url" content="{_e(abstract_html_url)}">',
        f'<meta property="og:site_name" content="{_e(journal_title)}">',
    ]

    # JSON-LD
    import json as _json
    jsonld = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": title,
        "abstract": abstract,
        "author": [
            {
                "@type": "Person",
                "name": a["name"],
                **({"identifier": f"https://orcid.org/{a['orcid']}"} if a["orcid"] else {}),
                **({"affiliation": {"@type": "Organization", "name": a["affiliation"]}} if a["affiliation"] else {}),
            }
            for a in authors
        ],
        "datePublished": article.published_date.isoformat() if article.published_date else None,
        "inLanguage": lang,
        "isAccessibleForFree": True,
        "isPartOf": {
            "@type": "Periodical",
            "name": journal_title,
            **({"issn": issn} if issn else {}),
        },
        "url": abstract_html_url,
        **({"identifier": {"@type": "PropertyValue", "propertyID": "DOI", "value": article.doi}} if article.doi else {}),
    }

    # ── Body content (for bots that render body only) ──
    authors_html = "".join(f"<li>{_e(a['name'])}{(', <em>' + _e(a['affiliation']) + '</em>') if a['affiliation'] else ''}</li>" for a in authors)
    keywords_html = ", ".join(_e(k) for k in keywords)
    refs_html = "".join(f"<li>{_e(r)}</li>" for r in references)
    volume_issue_str = ""
    if volume_num:
        volume_issue_str = f"Volume {volume_num}"
        if issue_num:
            volume_issue_str += f", Issue {issue_num}"

    html_doc = f"""<!DOCTYPE html>
<html lang="{_e(lang)}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_e(title)} | {_e(journal_title)}</title>
<meta name="description" content="{_e(abstract[:200])}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{_e(abstract_html_url)}">
{chr(10).join(citation_meta)}
{chr(10).join(og_meta)}
<script type="application/ld+json">
{_json.dumps(jsonld, ensure_ascii=False, default=str)}
</script>
<style>
body {{ font-family: Georgia, serif; max-width: 780px; margin: 2em auto; padding: 0 1em; line-height: 1.55; color: #111; }}
h1 {{ font-size: 1.7rem; line-height: 1.25; }}
ul.authors {{ padding-left: 1.2em; }}
ul.authors li {{ margin-bottom: .25em; }}
.meta {{ color: #555; font-size: .9em; margin: 1em 0; }}
.meta span {{ margin-right: 1em; }}
.abstract {{ background: #fafaf5; border-left: 3px solid #333; padding: .8em 1em; margin: 1.5em 0; }}
.keywords {{ font-size: .9em; color: #444; }}
ol.refs {{ font-size: .9em; color: #333; }}
.doi a {{ color: #0466c8; }}
</style>
</head>
<body>
<h1>{_e(title)}</h1>
{('<ul class="authors">' + authors_html + '</ul>') if authors_html else ''}
<p class="meta">
  {('<span><strong>Journal:</strong> ' + _e(journal_title) + '</span>') if journal_title else ''}
  {('<span>' + _e(volume_issue_str) + '</span>') if volume_issue_str else ''}
  {('<span><strong>Pages:</strong> ' + _e(article.pages) + '</span>') if article.pages else ''}
  {('<span><strong>Published:</strong> ' + _e(article.published_date.strftime("%Y-%m-%d")) + '</span>') if article.published_date else ''}
  {('<span><strong>Language:</strong> ' + _e(lang) + '</span>') if lang else ''}
</p>
{('<div class="doi"><strong>DOI:</strong> <a href="https://doi.org/' + _e(article.doi) + '">https://doi.org/' + _e(article.doi) + '</a></div>') if article.doi else ''}
{('<div class="abstract"><h2>Abstract</h2><p>' + _e(abstract) + '</p></div>') if abstract else ''}
{('<p class="keywords"><strong>Keywords:</strong> ' + keywords_html + '</p>') if keywords_html else ''}
{('<h2>References</h2><ol class="refs">' + refs_html + '</ol>') if refs_html else ''}
{('<p><a href="' + _e(pdf_url) + '">Download PDF</a></p>') if pdf_url else ''}
<hr>
<p><small>Full article: <a href="{_e(abstract_html_url)}">{_e(abstract_html_url)}</a></small></p>
</body>
</html>
"""

    return HTMLResponse(
        content=html_doc,
        headers={
            "Cache-Control": "public, max-age=3600",
            "X-Robots-Tag": "index, follow",
        },
    )
