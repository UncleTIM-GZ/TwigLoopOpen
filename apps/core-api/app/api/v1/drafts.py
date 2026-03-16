"""Draft routes — CRUD for AI-assisted drafts."""

import uuid

from fastapi import APIRouter, Depends
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.draft import (
    CreateDraftRequest,
    DraftResponse,
    UpdateDraftRequest,
)
from app.services.draft_service import DraftService

router = APIRouter(prefix="/drafts", tags=["drafts"])


@router.post("/", status_code=201)  # type: ignore[untyped-decorator]
async def create_draft(
    body: CreateDraftRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[DraftResponse]:
    service = DraftService(session)
    result = await service.create_draft(body, user)
    return ApiResponse(success=True, data=result)


@router.get("/")  # type: ignore[untyped-decorator]
async def list_my_drafts(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[DraftResponse]]:
    service = DraftService(session)
    items = await service.list_my_drafts(user)
    return ApiResponse(success=True, data=items)


@router.get("/{draft_id}")  # type: ignore[untyped-decorator]
async def get_draft(
    draft_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[DraftResponse]:
    service = DraftService(session)
    result = await service.get_draft(draft_id, user)
    return ApiResponse(success=True, data=result)


@router.patch("/{draft_id}")  # type: ignore[untyped-decorator]
async def update_draft(
    draft_id: uuid.UUID,
    body: UpdateDraftRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[DraftResponse]:
    service = DraftService(session)
    result = await service.update_draft(draft_id, body, user)
    return ApiResponse(success=True, data=result)


@router.delete("/{draft_id}")  # type: ignore[untyped-decorator]
async def delete_draft(
    draft_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, str]]:
    service = DraftService(session)
    await service.delete_draft(draft_id, user)
    return ApiResponse(success=True, data={"deleted": str(draft_id)})
