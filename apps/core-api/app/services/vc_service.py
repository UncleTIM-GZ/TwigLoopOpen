"""VerifiableCredential service — issue, query, verify."""

import logging
import uuid
from datetime import UTC, datetime

from shared_auth import CurrentUser
from shared_events import Subjects, publish_event
from shared_schemas import PaginatedMeta
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.verifiable_credential import VerifiableCredential
from app.repositories.project_repo import ProjectRepository
from app.repositories.task_card_repo import TaskCardRepository
from app.repositories.vc_repo import VerifiableCredentialRepository
from app.schemas.credential import (
    CredentialResponse,
    IssueCredentialRequest,
    VerifyResponse,
)
from app.services.event_write_service import EventWriteService

logger = logging.getLogger(__name__)

VALID_CREDENTIAL_TYPES = {"task_completion", "project_participation"}


class VerifiableCredentialService:
    def __init__(self, session: AsyncSession) -> None:
        self._vc_repo = VerifiableCredentialRepository(session)
        self._project_repo = ProjectRepository(session)
        self._task_repo = TaskCardRepository(session)
        self._events = EventWriteService(session)

    async def issue(self, req: IssueCredentialRequest, user: CurrentUser) -> CredentialResponse:
        if req.credential_type not in VALID_CREDENTIAL_TYPES:
            raise ConflictError(f"Invalid credential type: {req.credential_type}")

        # Authorization: only issue for self, or project owner can issue for collaborators
        if req.actor_id != user.actor_id:
            if req.project_id:
                project = await self._project_repo.find_by_id(req.project_id)
                if not project or project.founder_actor_id != user.actor_id:
                    raise ForbiddenError("Cannot issue credential for another actor")
            else:
                raise ForbiddenError("Cannot issue credential for another actor")

        credential_data = await self._build_credential_data(req)

        vc = VerifiableCredential(
            actor_id=req.actor_id,
            project_id=req.project_id,
            task_id=req.task_id,
            credential_type=req.credential_type,
            credential_data_json=credential_data,
            status="issued",
            issued_at=datetime.now(UTC),
        )
        vc = await self._vc_repo.create(vc)

        await publish_event(
            Subjects.CREDENTIAL_ISSUED,
            {"credential_id": str(vc.id), "credential_type": req.credential_type},
            actor_id=user.actor_id,
        )

        try:
            await self._events.record_domain_event(
                "credential_issued",
                "verifiable_credential",
                vc.id,
                actor_id=user.actor_id,
                payload={"credential_type": req.credential_type},
            )
        except Exception:
            logger.warning(
                "Side-effect failed: credential_issued for vc=%s (actor=%s)",
                vc.id,
                user.actor_id,
                exc_info=True,
            )

        return self._to_response(vc)

    async def get_by_id(self, vc_id: uuid.UUID, user: CurrentUser) -> CredentialResponse:
        vc = await self._vc_repo.find_by_id(vc_id)
        if not vc:
            raise NotFoundError("Credential not found")
        # Only holder or project founder can view credential details
        if vc.actor_id != user.actor_id:
            if vc.project_id:
                project = await self._project_repo.find_by_id(vc.project_id)
                if not project or project.founder_actor_id != user.actor_id:
                    raise ForbiddenError("Not authorized to view this credential")
            else:
                raise ForbiddenError("Not authorized to view this credential")
        return self._to_response(vc)

    async def verify(self, vc_id: uuid.UUID) -> VerifyResponse:
        vc = await self._vc_repo.find_by_id(vc_id)
        if not vc or vc.status != "issued":
            return VerifyResponse(valid=False)
        return VerifyResponse(
            valid=True,
            credential_type=vc.credential_type,
            issued_at=vc.issued_at,
        )

    async def list_for_actor(self, user: CurrentUser) -> list[CredentialResponse]:
        vcs = await self._vc_repo.find_by_actor(user.actor_id)
        return [self._to_response(vc) for vc in vcs]

    async def get_list_for_actor(
        self, user: CurrentUser, *, page: int = 1, limit: int = 20
    ) -> tuple[list[CredentialResponse], PaginatedMeta]:
        offset = (page - 1) * limit
        items, total = await self._vc_repo.find_paginated_by_actor(
            user.actor_id, offset=offset, limit=limit
        )
        meta = PaginatedMeta(
            total=total,
            page=page,
            limit=limit,
            has_next=(offset + limit) < total,
        )
        return [self._to_response(vc) for vc in items], meta

    async def _build_credential_data(self, req: IssueCredentialRequest) -> dict[str, object]:
        data: dict[str, object] = {
            "credential_type": req.credential_type,
            "actor_id": str(req.actor_id),
            "issued_at": datetime.now(UTC).isoformat(),
        }

        if req.project_id:
            project = await self._project_repo.find_by_id(req.project_id)
            if not project:
                raise NotFoundError("Project not found")
            if req.credential_type == "project_participation" and project.status != "delivered":
                raise ConflictError(
                    "Project must be in 'delivered' status to issue participation VC"
                )
            data["project_title"] = project.title
            data["project_id"] = str(req.project_id)

        if req.task_id:
            task = await self._task_repo.find_by_id(req.task_id)
            if not task:
                raise NotFoundError("Task not found")
            if req.credential_type == "task_completion" and task.status != "completed":
                raise ConflictError("Task must be in 'completed' status to issue completion VC")
            # Evidence-backed issuance gate: non-legacy tasks must be verified
            if (
                req.credential_type == "task_completion"
                and task.completion_mode != "legacy"
                and task.verification_status != "verified"
            ):
                raise ConflictError(
                    "Task must have verification_status 'verified' to issue completion VC"
                )
            data["task_title"] = task.title
            data["task_id"] = str(req.task_id)
            data["ewu"] = str(task.ewu)

        return data

    @staticmethod
    def _to_response(vc: VerifiableCredential) -> CredentialResponse:
        return CredentialResponse(
            credential_id=vc.id,
            actor_id=vc.actor_id,
            project_id=vc.project_id,
            task_id=vc.task_id,
            credential_type=vc.credential_type,
            credential_data=vc.credential_data_json,
            status=vc.status,
            issued_at=vc.issued_at,
            created_at=vc.created_at,
        )
