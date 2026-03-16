"""Platform rules & help routes — placeholders until tables exist."""

from fastapi import APIRouter, HTTPException
from shared_schemas import ApiResponse

router = APIRouter(prefix="/platform", tags=["platform"])


@router.get("/rules")  # type: ignore[untyped-decorator]
async def get_rules() -> ApiResponse[list[object]]:
    """Get platform rules. Placeholder — returns empty list until rules tables exist."""
    return ApiResponse(success=True, data=[])


@router.get("/help")  # type: ignore[untyped-decorator]
async def get_help_topics() -> ApiResponse[list[object]]:
    """Get help topics. Placeholder — returns empty list until help tables exist."""
    return ApiResponse(success=True, data=[])


@router.get("/help/{topic_key}")  # type: ignore[untyped-decorator]
async def get_help_topic(topic_key: str) -> ApiResponse[None]:
    """Get help topic detail. Placeholder."""
    raise HTTPException(status_code=404, detail="Help topics not yet implemented")
