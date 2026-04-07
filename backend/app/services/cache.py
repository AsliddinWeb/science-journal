"""
Redis-backed cache service.
Key naming convention:
  article:{uuid}          — single article detail, TTL 3600s
  articles:{hash}         — paginated article list, TTL 300s
  stats:overview          — site-wide stats, TTL 300s
  sitemap                 — rendered sitemap XML, TTL 3600s
  og:{article_id}         — OG image bytes as hex, TTL 86400s
"""
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            import redis.asyncio as aioredis
            from app.config import settings
            _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as exc:
            logger.warning("Redis not available: %s", exc)
    return _redis_client


async def get_cached(key: str) -> Optional[str]:
    """Return cached string value or None."""
    r = _get_redis()
    if r is None:
        return None
    try:
        return await r.get(key)
    except Exception as exc:
        logger.debug("Cache get error for key=%s: %s", key, exc)
        return None


async def set_cached(key: str, value: str, ttl: int = 300) -> None:
    """Store string value with TTL (seconds)."""
    r = _get_redis()
    if r is None:
        return
    try:
        await r.setex(key, ttl, value)
    except Exception as exc:
        logger.debug("Cache set error for key=%s: %s", key, exc)


async def invalidate(key: str) -> None:
    """Delete a single cache key."""
    r = _get_redis()
    if r is None:
        return
    try:
        await r.delete(key)
    except Exception as exc:
        logger.debug("Cache invalidate error for key=%s: %s", key, exc)


async def invalidate_prefix(prefix: str) -> None:
    """Delete all keys matching prefix* using SCAN to avoid blocking."""
    r = _get_redis()
    if r is None:
        return
    try:
        cursor = 0
        while True:
            cursor, keys = await r.scan(cursor=cursor, match=f"{prefix}*", count=100)
            if keys:
                await r.delete(*keys)
            if cursor == 0:
                break
    except Exception as exc:
        logger.debug("Cache invalidate_prefix error for prefix=%s: %s", prefix, exc)
