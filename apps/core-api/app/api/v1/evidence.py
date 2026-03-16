"""Evidence and verification routes."""

import uuid

from fastapi import APIRouter, Depends
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.evidence import (
    EvidenceResponse,
    SubmitEvidenceRequest,
    VerificationResponse,
    VerifyTaskRequest,
)
from app.services.evidence_service import EvidenceService

router = APIRouter(tags=["evidence"])


@router.post("/tasks/{task_id}/evidence", status_code=201)  # type: ignore[untyped-decorator]
async def submit_evidence(
    task_id: uuid.UUID,
    body: SubmitEvidenceRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[EvidenceResponse]:
    service = EvidenceService(session)
    result = await service.submit_evidence(task_id, body, user)
    return ApiResponse(success=True, data=result)


@router.get("/tasks/{task_id}/evidence")  # type: ignore[untyped-decorator]
async def list_evidence(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[EvidenceResponse]]:
    service = EvidenceService(session)
    items = await service.list_evidence(task_id)
    return ApiResponse(success=True, data=items)


@router.post("/tasks/{task_id}/verify", status_code=201)  # type: ignore[untyped-decorator]
async def verify_task(
    task_id: uuid.UUID,
    body: VerifyTaskRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[VerificationResponse]:
    service = EvidenceService(session)
    result = await service.verify_task(task_id, body, user)
    return ApiResponse(success=True, data=result)


@router.get("/tasks/{task_id}/verification")  # type: ignore[untyped-decorator]
async def list_verifications(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[VerificationResponse]]:
    service = EvidenceService(session)
    items = await service.list_verifications(task_id)
    return ApiResponse(success=True, data=items)
