"""A2A coordination API — trigger agent delegations and view results."""

import uuid

from fastapi import APIRouter, Depends
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.domain.a2a_protocol import TaskEnvelope
from app.exceptions import NotFoundError
from app.repositories.evidence_repo import EvidenceRepository
from app.repositories.task_card_repo import TaskCardRepository
from app.repositories.work_package_repo import WorkPackageRepository
from app.services.coordination_service import CoordinationService

router = APIRouter(prefix="/a2a", tags=["a2a"])


@router.post("/tasks/{task_id}/match")
async def request_matching(
    task_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict]:
    """Request matching suggestions for a task via A2A delegation."""
    task_repo = TaskCardRepository(session)
    wp_repo = WorkPackageRepository(session)

    task = await task_repo.find_by_id(task_id)
    if not task:
        raise NotFoundError("Task not found")

    wp = await wp_repo.find_by_id(task.work_package_id)

    envelope = TaskEnvelope(
        task_id=str(task.id),
        project_id=str(wp.project_id) if wp else "",
        work_package_id=str(task.work_package_id),
        actor_id=str(user.actor_id),
        actor_role="founder",
        objective=task.goal,
        current_status=task.status,
        constraints={
            "task_type": task.task_type,
            "main_role": task.main_role,
            "risk_level": task.risk_level,
            "ewu": str(task.ewu),
        },
        completion_criteria=task.completion_criteria,
    )

    coord = CoordinationService(session)
    result = await coord.delegate_matching(envelope)

    return ApiResponse(
        success=True,
        data={
            "delegation_id": result.delegation_id,
            "result_type": result.result_type,
            "summary": result.summary,
            "suggestions": result.structured_payload,
            "confidence": result.confidence,
            "requires_human_review": result.requires_human_review,
        },
    )


@router.post("/tasks/{task_id}/review-prep")
async def request_review_prep(
    task_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict]:
    """Request review preparation brief via A2A delegation."""
    task_repo = TaskCardRepository(session)
    wp_repo = WorkPackageRepository(session)
    evidence_repo = EvidenceRepository(session)

    task = await task_repo.find_by_id(task_id)
    if not task:
        raise NotFoundError("Task not found")

    wp = await wp_repo.find_by_id(task.work_package_id)
    evidence_count = await evidence_repo.count_by_task(task_id)

    envelope = TaskEnvelope(
        task_id=str(task.id),
        project_id=str(wp.project_id) if wp else "",
        work_package_id=str(task.work_package_id),
        actor_id=str(user.actor_id),
        actor_role="reviewer",
        objective=task.goal,
        current_status=task.status,
        completion_criteria=task.completion_criteria,
        evidence_requirements=["code_pr", "document"],
        signal_context={
            "evidence_count": evidence_count,
            "repo_url": task.repo_url,
            "ewu": str(task.ewu),
        },
    )

    coord = CoordinationService(session)
    result = await coord.delegate_review_prep(envelope)

    return ApiResponse(
        success=True,
        data={
            "delegation_id": result.delegation_id,
            "result_type": result.result_type,
            "summary": result.summary,
            "review_brief": result.structured_payload,
            "confidence": result.confidence,
            "requires_human_review": result.requires_human_review,
        },
    )
