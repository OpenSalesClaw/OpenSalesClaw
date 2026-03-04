from typing import Any, Generic, TypeVar

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

    @classmethod
    def from_result(
        cls,
        items: list[Any],
        total: int,
        pagination: "PaginationParams",
    ) -> "PaginatedResponse[Any]":
        """Convenience constructor from a (items, total) service result."""
        return cls(items=items, total=total, offset=pagination.offset, limit=pagination.limit)
