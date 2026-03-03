from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")

_DEFAULT_LIMIT = 20
_MAX_LIMIT = 200


class PaginationParams:
    """FastAPI dependency for offset/limit pagination query parameters."""

    def __init__(
        self,
        offset: int = Query(default=0, ge=0, description="Number of records to skip"),
        limit: int = Query(default=_DEFAULT_LIMIT, ge=1, le=_MAX_LIMIT, description="Maximum number of records"),
    ) -> None:
        self.offset = offset
        self.limit = limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response envelope."""

    items: list[T]
    total: int
    offset: int
    limit: int
