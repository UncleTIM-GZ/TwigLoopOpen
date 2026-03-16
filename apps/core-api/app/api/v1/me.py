"""User profile routes — GET/PATCH /me."""

from fastapi import APIRouter, Depends, Query
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.credential import CredentialResponse
from app.schemas.user import ActorInfo, MeResponse, UpdateProfileRequest
from app.services.profile_service import ProfileService
from app.services.vc_service import VerifiableCredentialService

router = APIRouter(tags=["me"])


@router.get("/me")  # type: ignore[untyped-decorator]
async def get_me(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[MeResponse]:
    service = ProfileService(session)
    result = await service.get_profile(user)
    return ApiResponse(success=True, data=result)


@router.patch("/me")  # type: ignore[untyped-decorator]
async def update_me(
    body: UpdateProfileRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ActorInfo]:
    service = ProfileService(session)
    result = await service.update_profile(user, body)
    return ApiResponse(success=True, data=result)


@router.get("/me/credentials")  # type: ignore[untyped-decorator]
async def list_my_credentials(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[CredentialResponse]]:
    service = VerifiableCredentialService(session)
    results, meta = await service.get_list_for_actor(user, page=page, limit=limit)
    return ApiResponse(success=True, data=results, meta=meta.model_dump())
