"""A2A coordination API — trigger agent delegations and view results."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.domain.a2a_protocol import TaskEnvelope
from app.exceptions import ForbiddenError, NotFoundError
from app.repositories.evidence_repo import EvidenceRepository
from app.repositories.project_repo import ProjectRepository
from app.repositories.task_card_repo import TaskCardRepository
from app.repositories.work_package_repo import WorkPackageRepository
from app.services.coordination_service import CoordinationService

router = APIRouter(prefix="/a2a", tags=["a2a"])


async def _build_base_envelope(
    task_id: uuid.UUID,
    user: CurrentUser,
    session: AsyncSession,
    *,
    require_founder: bool = False,
) -> tuple[TaskEnvelope, Any, TaskCardRepository]:
    """Build base TaskEnvelope from task. Shared by all A2A endpoints."""
    task_repo = TaskCardRepository(session)
    wp_repo = WorkPackageRepository(session)

    task = await task_repo.find_by_id(task_id)
    if not task:
        raise NotFoundError("Task not found")

    wp = await wp_repo.find_by_id(task.work_package_id)

    if require_founder and wp:
        project_repo = ProjectRepository(session)
        project = await project_repo.find_by_id(wp.project_id)
        if project and project.founder_actor_id != user.actor_id:
            raise ForbiddenError("Only the project founder can trigger A2A delegations")

    envelope = TaskEnvelope(
        task_id=str(task.id),
        project_id=str(wp.project_id) if wp else "",
        work_package_id=str(task.work_package_id),
        actor_id=str(user.actor_id),
        objective=task.goal,
        current_status=task.status,
        completion_criteria=task.completion_criteria,
    )
    return envelope, task, task_repo


@router.post("/tasks/{task_id}/match")
async def request_matching(
    task_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict]:
    """Request matching suggestions for a task via A2A delegation."""
    envelope, task, _ = await _build_base_envelope(
        task_id,
        user,
        session,
        require_founder=True,
    )
    envelope.actor_role = "founder"
    envelope.constraints = {
        "task_type": task.task_type,
        "main_role": task.main_role,
        "risk_level": task.risk_level,
        "ewu": str(task.ewu),
    }

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
    envelope, task, _ = await _build_base_envelope(
        task_id,
        user,
        session,
        require_founder=True,
    )
    evidence_repo = EvidenceRepository(session)
    evidence_count = await evidence_repo.count_by_task(task_id)

    envelope.actor_role = "reviewer"
    envelope.evidence_requirements = ["code_pr", "document"]
    envelope.signal_context = {
        "evidence_count": evidence_count,
        "repo_url": task.repo_url,
        "ewu": str(task.ewu),
    }

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


@router.post("/tasks/{task_id}/github-signal")
async def request_github_signal(
    task_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict]:
    """Analyze GitHub signals for a task via A2A delegation."""
    envelope, task, task_repo = await _build_base_envelope(
        task_id,
        user,
        session,
        require_founder=True,
    )
    envelope.signal_context = {
        "repo_url": task.repo_url or "",
        "branch_name": task.branch_name or "",
        "pr_url": task.pr_url or "",
        "latest_commit_sha": task.latest_commit_sha or "",
        "signal_count": task.signal_count,
    }

    coord = CoordinationService(session)
    result = await coord.delegate_github_signal(envelope)

    # Write signal fields back to task
    updates: dict[str, object] = {}
    payload = result.structured_payload
    if payload.get("signal_status"):
        updates["signal_count"] = payload.get("signal_count", 0)
    if updates:
        await task_repo.update_fields(task, updates)

    return ApiResponse(
        success=True,
        data={
            "delegation_id": result.delegation_id,
            "result_type": result.result_type,
            "summary": result.summary,
            "signal_snapshot": result.structured_payload,
            "confidence": result.confidence,
        },
    )


@router.post("/tasks/{task_id}/vc-check")
async def request_vc_check(
    task_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict]:
    """Check VC issuance eligibility via A2A delegation."""
    envelope, task, _ = await _build_base_envelope(
        task_id,
        user,
        session,
        require_founder=True,
    )
    evidence_repo = EvidenceRepository(session)
    evidence_count = await evidence_repo.count_by_task(task_id)

    envelope.constraints = {"ewu": str(task.ewu)}
    envelope.signal_context = {
        "verification_status": task.verification_status,
        "completion_mode": task.completion_mode,
        "evidence_count": evidence_count,
        "target_actor_id": str(user.actor_id),
    }

    coord = CoordinationService(session)
    result = await coord.delegate_vc_issuance(envelope)

    return ApiResponse(
        success=True,
        data={
            "delegation_id": result.delegation_id,
            "result_type": result.result_type,
            "summary": result.summary,
            "vc_recommendation": result.structured_payload,
            "confidence": result.confidence,
            "requires_human_review": result.requires_human_review,
        },
    )
