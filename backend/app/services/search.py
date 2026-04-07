from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.models.article import Article, ArticleStatus


async def full_text_search(
    query: str,
    db: AsyncSession,
    limit: int = 10,
    offset: int = 0,
) -> tuple[list, int]:
    """
    Perform PostgreSQL full-text search across article titles and abstracts.
    Uses tsvector search on JSONB fields.
    """
    search_query = func.plainto_tsquery("simple", query)

    # Build base query filtering published articles
    stmt = (
        select(Article)
        .where(
            Article.status == ArticleStatus.published,
            func.to_tsvector(
                "simple",
                func.coalesce(
                    Article.title.op("->>")("uz"), ""
                ) + " " +
                func.coalesce(
                    Article.title.op("->>")("ru"), ""
                ) + " " +
                func.coalesce(
                    Article.title.op("->>")("en"), ""
                )
            ).op("@@")(search_query)
        )
        .order_by(Article.published_date.desc())
    )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all(), total
