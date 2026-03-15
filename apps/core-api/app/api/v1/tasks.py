"""Task card routes."""

import uuid

from fastapi import APIRouter, Depends, Query
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.domain.ewu import EwuInput
from app.schemas.status import EwuCalculateRequest, EwuCalculateResponse, StatusTransitionRequest
from app.schemas.task_card import CreateTaskCardRequest, TaskCardResponse, UpdateTaskCardRequest
from app.services.task_card_service import TaskCardService

router = APIRouter(tags=["tasks"])


@router.post("/work-packages/{wp_id}/tasks", status_code=201)  # type: ignore[untyped-decorator]
async def create_task(
    wp_id: uuid.UUID,
    body: CreateTaskCardRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[TaskCardResponse]:
    service = TaskCardService(session)
    result = await service.create(wp_id, body, user)
    return ApiResponse(success=True, data=result)


@router.get("/projects/{project_id}/tasks")  # type: ignore[untyped-decorator]
async def list_tasks(
    project_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[TaskCardResponse]]:
    service = TaskCardService(session)
    items, meta = await service.get_list(project_id, page=page, limit=limit)
    return ApiResponse(success=True, data=items, meta=meta.model_dump())


@router.patch("/tasks/{task_id}")  # type: ignore[untyped-decorator]
async def update_task(
    task_id: uuid.UUID,
    body: UpdateTaskCardRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[TaskCardResponse]:
    service = TaskCardService(session)
    result = await service.update(task_id, body, user)
    return ApiResponse(success=True, data=result)


@router.patch("/tasks/{task_id}/status")  # type: ignore[untyped-decorator]
async def transition_task_status(
    task_id: uuid.UUID,
    body: StatusTransitionRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[TaskCardResponse]:
    service = TaskCardService(session)
    result = await service.transition_status(task_id, body.status, user)
    return ApiResponse(success=True, data=result)


@router.post("/tasks/{task_id}/calculate-ewu")  # type: ignore[untyped-decorator]
async def calculate_task_ewu(
    task_id: uuid.UUID,
    body: EwuCalculateRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[EwuCalculateResponse]:
    service = TaskCardService(session)
    params = EwuInput(
        task_type=body.task_type,
        risk_level=body.risk_level,
        complexity=body.complexity,
        criticality=body.criticality,
        collaboration_complexity=body.collaboration_complexity,
    )
    result = await service.calculate_ewu(task_id, params, user)
    return ApiResponse(
        success=True,
        data=EwuCalculateResponse(ewu=result.ewu, breakdown=result.breakdown),
    )
