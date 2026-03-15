"""Sponsor routes — sponsor dashboard endpoints."""

from fastapi import APIRouter, Depends
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.sponsor import CreateSupportRequest, SupportResponse
from app.services.sponsor_service import SponsorService

router = APIRouter(prefix="/sponsors", tags=["sponsors"])


@router.post("/support", status_code=201)  # type: ignore[untyped-decorator]
async def create_support(
    body: CreateSupportRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[SupportResponse]:
    service = SponsorService(session)
    result = await service.create_support(body, user)
    return ApiResponse(success=True, data=result)


@router.get("/my-supports")  # type: ignore[untyped-decorator]
async def list_my_supports(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[SupportResponse]]:
    service = SponsorService(session)
    items = await service.list_my_supports(user)
    return ApiResponse(success=True, data=items)
