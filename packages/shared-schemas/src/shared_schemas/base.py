"""Base schemas used across all services."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedMeta(BaseModel):
    """Pagination metadata for list responses."""

    total: int
    page: int
    limit: int
    has_next: bool


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""

    success: bool
    data: T | None = None
    error: str | None = None
    meta: dict[str, Any] | None = None
