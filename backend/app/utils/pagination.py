from typing import TypeVar, Generic, List
from pydantic import BaseModel
import math

HARD_LIMIT = 100
DEFAULT_LIMIT = 10

T = TypeVar("T")


class PaginationParams:
    """Dependency for pagination parameters."""

    def __init__(self, page: int = 1, limit: int = DEFAULT_LIMIT):
        self.page = max(1, page)
        self.limit = min(max(1, limit), HARD_LIMIT)
        self.offset = (self.page - 1) * self.limit


def paginate_response(items: list, total: int, page: int, limit: int) -> dict:
    """Build a standard paginated response dict."""
    pages = math.ceil(total / limit) if limit > 0 else 0
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }
