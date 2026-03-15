"""Source routes — bind/unbind repos, list sources and signals."""

import uuid

from fastapi import APIRouter, Depends, Query
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.signal import SignalResponse
from app.schemas.source import BindRepoRequest, SourceResponse
from app.services.signal_service import SignalService
from app.services.source_service import SourceService

router = APIRouter(tags=["sources"])


@router.post("/projects/{project_id}/sources", status_code=201)  # type: ignore[untyped-decorator]
async def bind_source(
    project_id: uuid.UUID,
    body: BindRepoRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[SourceResponse]:
    service = SourceService(session)
    result = await service.bind_repo(project_id, body, user)
    return ApiResponse(success=True, data=result)


@router.get("/projects/{project_id}/sources")  # type: ignore[untyped-decorator]
async def list_sources(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[SourceResponse]]:
    service = SourceService(session)
    result = await service.list_sources(project_id)
    return ApiResponse(success=True, data=result)


@router.delete("/sources/{source_id}", status_code=200)  # type: ignore[untyped-decorator]
async def unbind_source(
    source_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[None]:
    service = SourceService(session)
    await service.unbind_repo(source_id, user)
    return ApiResponse(success=True, data=None)


@router.get("/projects/{project_id}/signals")  # type: ignore[untyped-decorator]
async def list_signals(
    project_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[SignalResponse]]:
    service = SignalService(session)
    result = await service.list_by_project(project_id, limit=limit)
    return ApiResponse(success=True, data=result)
