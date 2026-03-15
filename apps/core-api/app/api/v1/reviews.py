"""Review routes — reviewer dashboard endpoints."""

import uuid

from fastapi import APIRouter, Depends
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.review import ReviewResponse, SubmitReviewRequest
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/pending")  # type: ignore[untyped-decorator]
async def list_pending_reviews(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ReviewResponse]]:
    service = ReviewService(session)
    items = await service.list_pending(user)
    return ApiResponse(success=True, data=items)


@router.post("/{project_id}/submit")  # type: ignore[untyped-decorator]
async def submit_review(
    project_id: uuid.UUID,
    body: SubmitReviewRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ReviewResponse]:
    service = ReviewService(session)
    result = await service.submit_review(project_id, body.decision, body.feedback, user)
    return ApiResponse(success=True, data=result)
