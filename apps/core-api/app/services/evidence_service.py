"""Evidence and verification service — submit evidence, review tasks."""

import logging
import uuid
from datetime import UTC, datetime

from shared_auth import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.delivery_evidence import DeliveryEvidence
from app.models.task_verification import TaskVerification
from app.repositories.evidence_repo import EvidenceRepository
from app.repositories.project_repo import ProjectRepository
from app.repositories.task_card_repo import TaskCardRepository
from app.repositories.verification_repo import VerificationRepository
from app.repositories.work_package_repo import WorkPackageRepository
from app.schemas.evidence import (
    EvidenceResponse,
    SubmitEvidenceRequest,
    VerificationResponse,
    VerifyTaskRequest,
)
from app.services.event_write_service import EventWriteService

logger = logging.getLogger(__name__)


class EvidenceService:
    def __init__(self, session: AsyncSession) -> None:
        self._evidence_repo = EvidenceRepository(session)
        self._verification_repo = VerificationRepository(session)
        self._task_repo = TaskCardRepository(session)
        self._wp_repo = WorkPackageRepository(session)
        self._project_repo = ProjectRepository(session)
        self._events = EventWriteService(session)

    async def submit_evidence(
        self, task_id: uuid.UUID, req: SubmitEvidenceRequest, user: CurrentUser
    ) -> EvidenceResponse:
        task = await self._task_repo.find_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")

        self._check_can_submit(task)

        # Determine version: increment from previous evidence on same task
        existing = await self._evidence_repo.find_by_task(task_id)
        version = len(existing) + 1

        # Mark previous latest as not-latest
        for ev in existing:
            if ev.is_latest:
                await self._evidence_repo.update_fields(ev, {"is_latest": False})

        evidence = DeliveryEvidence(
            task_id=task_id,
            actor_id=user.actor_id,
            evidence_type=req.evidence_type,
            title=req.title,
            description=req.description,
            evidence_url=req.evidence_url,
            evidence_source=req.evidence_source,
            version=version,
            is_latest=True,
            status="submitted",
        )
        evidence = await self._evidence_repo.create(evidence)

        try:
            await self._events.record_domain_event(
                "evidence_submitted",
                "delivery_evidence",
                evidence.id,
                actor_id=user.actor_id,
                payload={"task_id": str(task_id)},
            )
        except Exception:
            logger.warning(
                "Side-effect failed: evidence_submitted for evidence=%s (actor=%s)",
                evidence.id,
                user.actor_id,
                exc_info=True,
            )

        logger.info(
            "Evidence submitted",
            extra={
                "task_id": str(task_id),
                "actor_id": str(user.actor_id),
                "evidence_type": req.evidence_type,
                "evidence_id": str(evidence.id),
            },
        )

        return self._to_evidence_response(evidence)

    async def list_evidence(self, task_id: uuid.UUID) -> list[EvidenceResponse]:
        task = await self._task_repo.find_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        items = await self._evidence_repo.find_by_task(task_id)
        return [self._to_evidence_response(ev) for ev in items]

    async def verify_task(
        self, task_id: uuid.UUID, req: VerifyTaskRequest, user: CurrentUser
    ) -> VerificationResponse:
        task = await self._task_repo.find_by_id_for_update(task_id)
        if not task:
            raise NotFoundError("Task not found")

        # Authorization: only founder or reviewer can verify
        wp = await self._wp_repo.find_by_id(task.work_package_id)
        if not wp:
            raise NotFoundError("Work package not found")
        project = await self._project_repo.find_by_id(wp.project_id)
        if not project:
            raise NotFoundError("Project not found")
        if project.founder_actor_id != user.actor_id and "reviewer" not in user.roles:
            raise ForbiddenError("Only the project founder or a reviewer can verify tasks")

        # Find latest evidence for the task (optional — verification can happen without)
        latest_evidence = await self._evidence_repo.find_latest_by_task(task_id)
        evidence_id = latest_evidence.id if latest_evidence else None

        verification = TaskVerification(
            task_id=task_id,
            evidence_id=evidence_id,
            reviewer_id=user.actor_id,
            decision=req.decision,
            note=req.note,
        )
        verification = await self._verification_repo.create(verification)

        # Update task verification status based on decision
        now = datetime.now(UTC)
        if req.decision == "approved":
            await self._task_repo.update_fields(
                task,
                {
                    "verification_status": "verified",
                    "verified_at": now,
                    "verified_by": user.actor_id,
                },
            )
        elif req.decision == "rejected":
            await self._task_repo.update_fields(task, {"verification_status": "rejected"})
        elif req.decision == "needs_revision":
            updates: dict[str, object] = {"verification_status": "unverified"}
            # If currently under_review, transition back to rework_required
            if task.status == "under_review":
                updates["status"] = "rework_required"
            await self._task_repo.update_fields(task, updates)

        try:
            await self._events.record_domain_event(
                "task_verified",
                "task_verification",
                verification.id,
                actor_id=user.actor_id,
                payload={
                    "task_id": str(task_id),
                    "decision": req.decision,
                },
            )
        except Exception:
            logger.warning(
                "Side-effect failed: task_verified for verification=%s (actor=%s)",
                verification.id,
                user.actor_id,
                exc_info=True,
            )

        logger.info(
            "Task verification decided",
            extra={
                "task_id": str(task_id),
                "reviewer_id": str(user.actor_id),
                "decision": req.decision,
                "verification_status": task.verification_status,
            },
        )

        return self._to_verification_response(verification)

    async def list_verifications(self, task_id: uuid.UUID) -> list[VerificationResponse]:
        task = await self._task_repo.find_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        items = await self._verification_repo.find_by_task(task_id)
        return [self._to_verification_response(v) for v in items]

    @staticmethod
    def _check_can_submit(task: object) -> None:
        """Ensure the task is in a state that allows evidence submission."""
        status = getattr(task, "status", None)
        if status not in ("in_progress", "submitted", "under_review", "rework_required"):
            raise ConflictError(
                f"Cannot submit evidence for task in '{status}' status. "
                "Task must be in_progress, submitted, under_review, or rework_required."
            )

    @staticmethod
    def _to_evidence_response(ev: DeliveryEvidence) -> EvidenceResponse:
        return EvidenceResponse(
            evidence_id=ev.id,
            task_id=ev.task_id,
            actor_id=ev.actor_id,
            evidence_type=ev.evidence_type,
            title=ev.title,
            description=ev.description,
            evidence_url=ev.evidence_url,
            evidence_source=ev.evidence_source,
            version=ev.version,
            is_latest=ev.is_latest,
            status=ev.status,
            reviewer_note=ev.reviewer_note,
            created_at=ev.created_at,
        )

    @staticmethod
    def _to_verification_response(v: TaskVerification) -> VerificationResponse:
        return VerificationResponse(
            verification_id=v.id,
            task_id=v.task_id,
            evidence_id=v.evidence_id,
            reviewer_id=v.reviewer_id,
            decision=v.decision,
            note=v.note,
            created_at=v.created_at,
        )
