"""Review service — business logic for public-benefit project reviews."""

import uuid

from shared_auth import CurrentUser
from shared_events import Subjects, publish_event
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError, ForbiddenError, NotFoundError
from app.models.review_record import ReviewRecord
from app.repositories.actor_repo import ActorRepository
from app.repositories.project_repo import ProjectRepository
from app.repositories.review_record_repo import ReviewRecordRepository
from app.schemas.review import ReviewResponse


class ReviewService:
    def __init__(self, session: AsyncSession) -> None:
        self._project_repo = ProjectRepository(session)
        self._actor_repo = ActorRepository(session)
        self._review_repo = ReviewRecordRepository(session)

    async def list_pending(self, user: CurrentUser) -> list[ReviewResponse]:
        """List projects pending human review for the current reviewer."""
        actor = await self._actor_repo.find_by_id(user.actor_id)
        if not actor or not actor.is_reviewer:
            raise ForbiddenError("Only reviewers can access pending reviews")

        pending, _total = await self._project_repo.find_list(
            project_type="public_benefit",
            human_review_status="reviewer_required",
            offset=0,
            limit=100,
        )

        return [
            ReviewResponse(
                project_id=p.id,
                reviewer_actor_id=user.actor_id,
                decision="pending",
                feedback=None,
                created_at=p.created_at,
            )
            for p in pending
        ]

    async def submit_review(
        self,
        project_id: uuid.UUID,
        decision: str,
        feedback: str | None,
        user: CurrentUser,
    ) -> ReviewResponse:
        """Submit a review decision for a project."""
        actor = await self._actor_repo.find_by_id(user.actor_id)
        if not actor or not actor.is_reviewer:
            raise ForbiddenError("Only reviewers can submit reviews")

        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        if project.human_review_status != "reviewer_required":
            raise ForbiddenError("Project does not require review")

        # Map decision to human_review_status
        status_map = {
            "passed": "human_review_passed",
            "needs_revision": "reviewer_required",
            "rejected": "rejected",
        }
        new_status = status_map.get(decision)
        if not new_status:
            raise AppError("Invalid review decision", status_code=400)
        await self._project_repo.update_fields(project, {"human_review_status": new_status})

        record = ReviewRecord(
            project_id=project_id,
            reviewer_actor_id=user.actor_id,
            decision=decision,
            feedback=feedback,
        )
        record = await self._review_repo.create(record)

        await publish_event(
            Subjects.REVIEW_SUBMITTED,
            {
                "project_id": str(project_id),
                "decision": decision,
                "reviewer_actor_id": str(user.actor_id),
            },
            actor_id=user.actor_id,
        )

        return ReviewResponse(
            project_id=record.project_id,
            reviewer_actor_id=record.reviewer_actor_id,
            decision=record.decision,
            feedback=record.feedback,
            created_at=record.created_at,
        )
