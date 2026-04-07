import json
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.article import Article, ArticleStatus
from app.models.user import User
from app.models.volume import Volume
from app.services.cache import get_cached, set_cached

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview")
async def get_overview_stats(db: AsyncSession = Depends(get_db)) -> dict:
    """Return site-wide statistics for the public homepage. Cached 300s."""
    cached = await get_cached("stats:overview")
    if cached:
        return json.loads(cached)

    total_articles = (
        await db.execute(
            select(func.count()).select_from(Article).where(Article.status == ArticleStatus.published)
        )
    ).scalar_one()

    total_authors = (
        await db.execute(
            select(func.count(func.distinct(Article.author_id)))
            .select_from(Article)
            .where(Article.status == ArticleStatus.published)
        )
    ).scalar_one()

    total_downloads = (
        await db.execute(
            select(func.coalesce(func.sum(Article.download_count), 0))
            .select_from(Article)
            .where(Article.status == ArticleStatus.published)
        )
    ).scalar_one()

    total_volumes = (
        await db.execute(select(func.count()).select_from(Volume))
    ).scalar_one()

    result = {
        "total_articles": total_articles,
        "total_authors": total_authors,
        "total_downloads": int(total_downloads),
        "total_volumes": total_volumes,
    }
    await set_cached("stats:overview", json.dumps(result), ttl=300)
    return result
