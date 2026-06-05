"""
OAI-PMH 2.0 repository endpoint — the standard interface that
Google Scholar, DOAJ, Crossref, and other indexers use to harvest
journal metadata in bulk.

We expose it at `/{journal_slug}/oai` to mirror the OJS convention
(e.g. publishscience.uz/sirsh/oai), since Scholar's crawler is tuned
to recognise that URL shape.

Supported verbs (spec: https://www.openarchives.org/OAI/openarchivesprotocol.html):
  - Identify
  - ListMetadataFormats
  - ListSets
  - ListIdentifiers
  - ListRecords
  - GetRecord

Supported metadata prefix: oai_dc (Dublin Core — the only required
format, and the one Scholar harvests).

All journal-level values (name, ISSN, contact, publisher) come from
HomeSettings; per-record values come from the Article model. Nothing
is hardcoded.
"""
from __future__ import annotations

import html as _html
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.article import Article, ArticleAuthor, ArticleStatus
from app.models.home_settings import HomeSettings

router = APIRouter(tags=["oai"])


# ─── XML helpers ─────────────────────────────────────────────────────────────

def _e(value: Any) -> str:
    """XML-escape a value; empty string for None."""
    if value is None:
        return ""
    return _html.escape(str(value), quote=True)


def _pick(d: dict | None, lang: str = "en") -> str:
    if not isinstance(d, dict):
        return ""
    return d.get(lang) or d.get("en") or d.get("uz") or d.get("ru") or ""


def _per_lang(d: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    if not isinstance(d, dict):
        return out
    for k in ("uz", "ru", "en"):
        v = d.get(k)
        if isinstance(v, list):
            v = ", ".join(str(x).strip() for x in v if x)
        if isinstance(v, str) and v.strip():
            out[k] = v.strip()
    return out


def _flatten(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if x]
    if isinstance(value, dict):
        out: list[str] = []
        for k in ("uz", "ru", "en"):
            part = value.get(k)
            if isinstance(part, list):
                out.extend(str(x).strip() for x in part if x)
        seen: set[str] = set()
        uniq: list[str] = []
        for x in out:
            if x and x not in seen:
                seen.add(x)
                uniq.append(x)
        return uniq
    return []


def _oai_datetime(dt: datetime | None) -> str:
    """OAI-PMH requires UTC ISO 8601 with second precision."""
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─── data loading ────────────────────────────────────────────────────────────

async def _load_settings(db: AsyncSession) -> dict:
    row = (await db.execute(select(HomeSettings).where(HomeSettings.id == "default"))).scalar_one_or_none()
    site_name_en = _pick(row.site_name, "en") if row else ""
    site_name_uz = _pick(row.site_name, "uz") if row else ""
    if not site_name_en and row:
        site_name_en = _pick(row.hero_title, "en")
    if not site_name_uz and row:
        site_name_uz = _pick(row.hero_title, "uz")
    return {
        "name": site_name_en or site_name_uz or "Journal",
        "name_uz": site_name_uz,
        "name_en": site_name_en,
        "journal_slug": (row.journal_slug if row and row.journal_slug else "academic-book-journal"),
        "issn_online": (row.issn_online or "").strip() if row else "",
        "issn_print": (row.issn_print or "").strip() if row else "",
        "license": (row.license_type or "").strip() if row else "",
        "admin_email": (row.contact_email or "").strip() if row else "",
    }


async def _load_articles(
    db: AsyncSession,
    *,
    only_id: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
) -> list[Article]:
    q = (
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.co_authors).selectinload(ArticleAuthor.user),
            selectinload(Article.volume),
            selectinload(Article.issue),
        )
        .where(Article.status == ArticleStatus.published)
        .order_by(Article.published_date.desc().nulls_last(), Article.created_at.desc())
    )
    if only_id:
        try:
            import uuid as _uuid
            q = q.where(Article.id == _uuid.UUID(only_id))
        except ValueError:
            return []
    else:
        q = q.offset(offset).limit(limit)
    res = await db.execute(q)
    return list(res.scalars().all())


# ─── record rendering ────────────────────────────────────────────────────────

def _oai_identifier(repo_id: str, article_id: str) -> str:
    return f"oai:{repo_id}:article/{article_id}"


def _article_authors(article: Article) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if article.author and article.author.role.value != "superadmin":
        out.append({
            "name": article.author.full_name or "",
            "affiliation": article.author.affiliation or "",
            "orcid": article.author.orcid_id or "",
        })
    for co in article.co_authors or []:
        name = (co.user.full_name if co.user else None) or co.guest_name or ""
        if not name:
            continue
        out.append({
            "name": name,
            "affiliation": (co.user.affiliation if co.user else None) or co.guest_affiliation or "",
            "orcid": (co.user.orcid_id if co.user else None) or co.guest_orcid or "",
        })
    return out


def _build_oai_dc(article: Article, cfg: dict, base_url: str) -> str:
    """Render the <metadata> body for one article in oai_dc format."""
    titles = _per_lang(article.title)
    abstracts = _per_lang(article.abstract)
    keywords = _flatten(article.keywords)
    authors = _article_authors(article)
    lang = getattr(article.language, "value", str(article.language)) if article.language else "en"
    abstract_url = f"{base_url}/{cfg['journal_slug']}/article/view/{article.id}"  # OJS-canonical

    pdf_path = article.pdf_file_path or ""
    if pdf_path:
        if not (pdf_path.startswith("http") or pdf_path.startswith("/")):
            pdf_path = f"/api/uploads/{pdf_path}"
        if pdf_path.startswith("/"):
            pdf_path = f"{base_url}{pdf_path}"

    parts: list[str] = []
    parts.append(
        '<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"'
        ' xmlns:dc="http://purl.org/dc/elements/1.1/"'
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        ' xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/'
        ' http://www.openarchives.org/OAI/2.0/oai_dc.xsd">'
    )
    # Title — primary + per-language variants
    primary_title = (
        _pick(article.title, lang)
        or _pick(article.title, "en")
        or _pick(article.title, "uz")
        or "Untitled"
    )
    parts.append(f"<dc:title>{_e(primary_title)}</dc:title>")
    for k, v in titles.items():
        if v != primary_title:
            parts.append(f'<dc:title xml:lang="{k}">{_e(v)}</dc:title>')
    # Creators
    for a in authors:
        if a["affiliation"]:
            parts.append(f'<dc:creator>{_e(a["name"])} ({_e(a["affiliation"])})</dc:creator>')
        else:
            parts.append(f"<dc:creator>{_e(a['name'])}</dc:creator>")
    # Subjects — keywords (per-language if available, else flat)
    kw_by_lang = _per_lang(article.keywords)
    if kw_by_lang:
        for k, v in kw_by_lang.items():
            parts.append(f'<dc:subject xml:lang="{k}">{_e(v)}</dc:subject>')
    else:
        for kw in keywords:
            parts.append(f"<dc:subject>{_e(kw)}</dc:subject>")
    # Descriptions — abstract per language
    if abstracts:
        for k, v in abstracts.items():
            parts.append(f'<dc:description xml:lang="{k}">{_e(v)}</dc:description>')
    elif _pick(article.abstract, lang):
        parts.append(f"<dc:description>{_e(_pick(article.abstract, lang))}</dc:description>")
    # Publisher
    if cfg.get("name"):
        parts.append(f"<dc:publisher>{_e(cfg['name'])}</dc:publisher>")
    # Date issued (publication date)
    pub_dt = article.published_date or article.created_at
    if pub_dt:
        parts.append(f"<dc:date>{_e(pub_dt.strftime('%Y-%m-%d'))}</dc:date>")
    # Type
    parts.append("<dc:type>info:eu-repo/semantics/article</dc:type>")
    parts.append("<dc:type>Text.Serial.Journal</dc:type>")
    # Format — PDF if present
    if pdf_path:
        parts.append("<dc:format>application/pdf</dc:format>")
    # Identifiers — HTML landing page, PDF, DOI
    parts.append(f"<dc:identifier>{_e(abstract_url)}</dc:identifier>")
    if pdf_path:
        parts.append(f"<dc:identifier>{_e(pdf_path)}</dc:identifier>")
    if article.doi:
        parts.append(f"<dc:identifier>https://doi.org/{_e(article.doi)}</dc:identifier>")
    # Source — journal name, ISSN, volume, issue, pages
    source_bits: list[str] = [cfg.get("name") or ""]
    if cfg.get("issn_online"):
        source_bits.append(cfg["issn_online"])
    if article.volume:
        source_bits.append(f"Vol. {article.volume.number}")
    if article.issue:
        source_bits.append(f"Issue {article.issue.number}")
    if article.pages:
        source_bits.append(f"pp. {article.pages}")
    source = "; ".join(b for b in source_bits if b)
    if source:
        parts.append(f"<dc:source>{_e(source)}</dc:source>")
    # Language
    parts.append(f"<dc:language>{_e(lang)}</dc:language>")
    # Rights (license)
    if cfg.get("license"):
        parts.append(f"<dc:rights>{_e(cfg['license'])}</dc:rights>")
    parts.append("<dc:rights>info:eu-repo/semantics/openAccess</dc:rights>")
    parts.append("</oai_dc:dc>")
    return "".join(parts)


def _render_record(article: Article, cfg: dict, base_url: str, repo_id: str) -> str:
    """Render a full <record> entry: header + metadata."""
    pub_dt = article.published_date or article.updated_at or article.created_at
    header = (
        "<header>"
        f"<identifier>{_e(_oai_identifier(repo_id, str(article.id)))}</identifier>"
        f"<datestamp>{_oai_datetime(pub_dt)}</datestamp>"
        "<setSpec>articles</setSpec>"
        "</header>"
    )
    metadata = f"<metadata>{_build_oai_dc(article, cfg, base_url)}</metadata>"
    return f"<record>{header}{metadata}</record>"


def _render_identifier(article: Article, repo_id: str) -> str:
    pub_dt = article.published_date or article.updated_at or article.created_at
    return (
        "<header>"
        f"<identifier>{_e(_oai_identifier(repo_id, str(article.id)))}</identifier>"
        f"<datestamp>{_oai_datetime(pub_dt)}</datestamp>"
        "<setSpec>articles</setSpec>"
        "</header>"
    )


# ─── envelope ────────────────────────────────────────────────────────────────

def _envelope(verb: str, request_url: str, params: dict[str, str], body: str) -> str:
    """Wrap a verb's response body in the standard OAI-PMH envelope."""
    request_attrs = " ".join(f'{k}="{_e(v)}"' for k, v in params.items() if v)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"'
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        ' xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/'
        ' http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">'
        f"<responseDate>{_now_iso()}</responseDate>"
        f'<request {request_attrs}>{_e(request_url)}</request>'
        f"{body}"
        "</OAI-PMH>"
    )


def _error(verb: str, request_url: str, params: dict[str, str], code: str, message: str = "") -> Response:
    body = f'<error code="{_e(code)}">{_e(message)}</error>'
    xml = _envelope(verb, request_url, params, body)
    return Response(content=xml, media_type="application/xml; charset=utf-8")


# ─── verbs ───────────────────────────────────────────────────────────────────

def _verb_identify(request_url: str, params: dict[str, str], cfg: dict, repo_id: str, earliest: str) -> str:
    body = (
        "<Identify>"
        f"<repositoryName>{_e(cfg['name'])}</repositoryName>"
        f"<baseURL>{_e(request_url)}</baseURL>"
        "<protocolVersion>2.0</protocolVersion>"
        f"<adminEmail>{_e(cfg.get('admin_email') or 'admin@' + request_url.split('//', 1)[-1].split('/', 1)[0])}</adminEmail>"
        f"<earliestDatestamp>{_e(earliest or '1970-01-01T00:00:00Z')}</earliestDatestamp>"
        "<deletedRecord>no</deletedRecord>"
        "<granularity>YYYY-MM-DDThh:mm:ssZ</granularity>"
        '<description>'
        '<oai-identifier xmlns="http://www.openarchives.org/OAI/2.0/oai-identifier"'
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        ' xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai-identifier'
        ' http://www.openarchives.org/OAI/2.0/oai-identifier.xsd">'
        '<scheme>oai</scheme>'
        f'<repositoryIdentifier>{_e(repo_id)}</repositoryIdentifier>'
        '<delimiter>:</delimiter>'
        f'<sampleIdentifier>oai:{_e(repo_id)}:article/00000000-0000-0000-0000-000000000000</sampleIdentifier>'
        '</oai-identifier>'
        '</description>'
        "</Identify>"
    )
    return _envelope("Identify", request_url, params, body)


def _verb_list_metadata_formats(request_url: str, params: dict[str, str]) -> str:
    body = (
        "<ListMetadataFormats>"
        "<metadataFormat>"
        "<metadataPrefix>oai_dc</metadataPrefix>"
        "<schema>http://www.openarchives.org/OAI/2.0/oai_dc.xsd</schema>"
        "<metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/</metadataNamespace>"
        "</metadataFormat>"
        "</ListMetadataFormats>"
    )
    return _envelope("ListMetadataFormats", request_url, params, body)


def _verb_list_sets(request_url: str, params: dict[str, str], cfg: dict) -> str:
    body = (
        "<ListSets>"
        "<set>"
        "<setSpec>articles</setSpec>"
        f"<setName>{_e(cfg['name'])} — Articles</setName>"
        "</set>"
        "</ListSets>"
    )
    return _envelope("ListSets", request_url, params, body)


# ─── route ───────────────────────────────────────────────────────────────────

@router.api_route("/{journal_slug}/oai", methods=["GET", "POST"], include_in_schema=False)
async def oai_pmh(
    journal_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """OAI-PMH 2.0 repository endpoint at /{journal_slug}/oai."""
    cfg = await _load_settings(db)
    # Politely 404 if a different slug was used.
    if journal_slug != cfg["journal_slug"]:
        return Response(status_code=404)

    base_url = str(settings.APP_URL).rstrip("/") if settings.APP_URL else f"{request.url.scheme}://{request.url.netloc}"
    request_url = f"{base_url}/{cfg['journal_slug']}/oai"
    # Derive a stable repository identifier from the public host.
    host = base_url.split("//", 1)[-1].split("/", 1)[0]
    repo_id = f"ojs2.{host}"

    # OAI accepts both GET and POST with the same parameter set.
    params: dict[str, str] = {}
    if request.method == "POST":
        form = await request.form()
        for k, v in form.items():
            params[k] = str(v)
    else:
        for k, v in request.query_params.items():
            params[k] = v

    verb = params.get("verb", "")

    if not verb:
        return _error("", request_url, {}, "badVerb", "Missing verb")

    metadata_prefix = params.get("metadataPrefix", "")
    identifier = params.get("identifier", "")
    resumption = params.get("resumptionToken", "")

    if verb == "Identify":
        # Earliest = oldest published article timestamp
        oldest = await db.execute(
            select(Article.published_date)
            .where(Article.status == ArticleStatus.published)
            .order_by(Article.published_date.asc().nulls_last())
            .limit(1)
        )
        oldest_dt = oldest.scalar_one_or_none()
        earliest = _oai_datetime(oldest_dt) if oldest_dt else ""
        xml = _verb_identify(request_url, {"verb": verb}, cfg, repo_id, earliest)
        return Response(content=xml, media_type="application/xml; charset=utf-8")

    if verb == "ListMetadataFormats":
        # If identifier given, validate it exists; spec allows scoped formats.
        if identifier:
            art_id = identifier.split(":")[-1].split("/", 1)[-1]
            arts = await _load_articles(db, only_id=art_id)
            if not arts:
                return _error(verb, request_url, params, "idDoesNotExist", "Unknown identifier")
        xml = _verb_list_metadata_formats(request_url, {"verb": verb, **({"identifier": identifier} if identifier else {})})
        return Response(content=xml, media_type="application/xml; charset=utf-8")

    if verb == "ListSets":
        xml = _verb_list_sets(request_url, {"verb": verb}, cfg)
        return Response(content=xml, media_type="application/xml; charset=utf-8")

    if verb == "GetRecord":
        if metadata_prefix != "oai_dc":
            return _error(verb, request_url, params, "cannotDisseminateFormat", "Only oai_dc is supported")
        if not identifier:
            return _error(verb, request_url, params, "badArgument", "Missing identifier")
        art_id = identifier.split(":")[-1].split("/", 1)[-1]
        arts = await _load_articles(db, only_id=art_id)
        if not arts:
            return _error(verb, request_url, params, "idDoesNotExist", "Unknown identifier")
        record = _render_record(arts[0], cfg, base_url, repo_id)
        body = f"<GetRecord>{record}</GetRecord>"
        xml = _envelope(verb, request_url, {"verb": verb, "identifier": identifier, "metadataPrefix": metadata_prefix}, body)
        return Response(content=xml, media_type="application/xml; charset=utf-8")

    if verb in ("ListIdentifiers", "ListRecords"):
        if metadata_prefix != "oai_dc" and not resumption:
            return _error(verb, request_url, params, "cannotDisseminateFormat", "Only oai_dc is supported")
        # Pagination via resumption token: "offset:limit"
        offset = 0
        limit = 100
        if resumption:
            try:
                off_s, lim_s = resumption.split(":")
                offset = int(off_s)
                limit = int(lim_s)
            except Exception:
                return _error(verb, request_url, params, "badResumptionToken", "Invalid token")
        articles = await _load_articles(db, offset=offset, limit=limit)
        if not articles and offset == 0:
            return _error(verb, request_url, params, "noRecordsMatch", "No published articles")
        items = (
            [_render_record(a, cfg, base_url, repo_id) for a in articles]
            if verb == "ListRecords"
            else [_render_identifier(a, repo_id) for a in articles]
        )
        # Emit a resumption token only when this batch was full — more may exist.
        token_xml = ""
        if len(articles) == limit:
            next_token = f"{offset + limit}:{limit}"
            token_xml = f"<resumptionToken>{_e(next_token)}</resumptionToken>"
        elif resumption:
            token_xml = "<resumptionToken/>"
        body = f"<{verb}>{''.join(items)}{token_xml}</{verb}>"
        echo_params = {"verb": verb}
        if metadata_prefix:
            echo_params["metadataPrefix"] = metadata_prefix
        if resumption:
            echo_params["resumptionToken"] = resumption
        xml = _envelope(verb, request_url, echo_params, body)
        return Response(content=xml, media_type="application/xml; charset=utf-8")

    return _error(verb, request_url, params, "badVerb", f"Unknown verb: {verb}")
