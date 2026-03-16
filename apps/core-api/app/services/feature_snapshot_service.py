"""Feature snapshot computation service — rule-based v1.

Computes structural features for actors and projects using simple aggregation rules.
No ML/graph algorithms — those are future phases.
"""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.actor import Actor
from app.models.application import ProjectApplication
from app.models.edges import ActorProjectEdge
from app.models.project import Project
from app.models.snapshots import ActorFeatureSnapshot, ProjectFeatureSnapshot
from app.models.task_card import TaskCard
from app.models.work_package import WorkPackage


class FeatureSnapshotService:
    """Compute and store feature snapshots for actors and projects."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Actor Snapshot ──────────────────────────────────────

    async def compute_actor_snapshot(self, actor_id: uuid.UUID) -> ActorFeatureSnapshot:
        """Compute feature snapshot for a single actor."""
        # Get latest version
        latest = await self._session.execute(
            select(func.coalesce(func.max(ActorFeatureSnapshot.version), 0)).where(
                ActorFeatureSnapshot.actor_id == actor_id
            )
        )
        next_version: int = latest.scalar_one() + 1

        # Compute features
        dominant_project_type = await self._actor_dominant_project_type(actor_id)
        dominant_task_type = await self._actor_dominant_task_type(actor_id)
        completion_rate = await self._actor_completion_rate(actor_id)
        reuse_count = await self._actor_reuse_count(actor_id)
        collab_breadth = await self._actor_collaboration_breadth(actor_id)
        coord_load = await self._actor_coordination_load(actor_id)
        pb_score = await self._actor_public_benefit_score(actor_id)
        review_score = await self._actor_review_reliability(actor_id)

        snapshot = ActorFeatureSnapshot(
            actor_id=actor_id,
            version=next_version,
            dominant_project_type=dominant_project_type,
            dominant_task_type=dominant_task_type,
            completion_rate=completion_rate,
            reuse_count=reuse_count,
            collaboration_breadth=collab_breadth,
            coordination_load_score=coord_load,
            public_benefit_participation_score=pb_score,
            review_reliability_score=review_score,
            feature_json={
                "version": next_version,
                "computed_at": datetime.now(UTC).isoformat(),
            },
        )
        self._session.add(snapshot)

        # Update denormalized fields on actor
        actor = (
            await self._session.execute(select(Actor).where(Actor.id == actor_id).with_for_update())
        ).scalar_one_or_none()
        if actor:
            actor.feature_snapshot_version = next_version  # type: ignore[assignment]
            actor.last_feature_computed_at = datetime.now(UTC)  # type: ignore[assignment]
            actor.dominant_project_type = dominant_project_type  # type: ignore[assignment]
            actor.dominant_task_type = dominant_task_type  # type: ignore[assignment]
            actor.completion_rate = completion_rate  # type: ignore[assignment]
            actor.reuse_count = reuse_count  # type: ignore[assignment]
            actor.collaboration_breadth = collab_breadth  # type: ignore[assignment]
            actor.coordination_load_score = coord_load  # type: ignore[assignment]

        await self._session.flush()
        return snapshot

    async def _actor_dominant_project_type(self, actor_id: uuid.UUID) -> str | None:
        """Most common project type the actor is involved with."""
        result = await self._session.execute(
            select(Project.project_type, func.count().label("cnt"))
            .join(ActorProjectEdge, ActorProjectEdge.project_id == Project.id)
            .where(ActorProjectEdge.actor_id == actor_id)
            .where(ActorProjectEdge.status == "active")
            .group_by(Project.project_type)
            .order_by(func.count().desc())
            .limit(1)
        )
        row = result.first()
        return row[0] if row else None

    async def _actor_dominant_task_type(self, actor_id: uuid.UUID) -> str | None:
        """Most common task type the actor has worked on."""
        result = await self._session.execute(
            select(TaskCard.task_type, func.count().label("cnt"))
            .join(WorkPackage, WorkPackage.id == TaskCard.work_package_id)
            .join(
                ProjectApplication,
                ProjectApplication.project_id == WorkPackage.project_id,
            )
            .where(ProjectApplication.actor_id == actor_id)
            .group_by(TaskCard.task_type)
            .order_by(func.count().desc())
            .limit(1)
        )
        row = result.first()
        return row[0] if row else None

    async def _actor_completion_rate(self, actor_id: uuid.UUID) -> Decimal | None:
        """Ratio of completed edges to total assigned edges."""
        result = await self._session.execute(
            select(
                func.count().filter(ActorProjectEdge.edge_type == "completed").label("completed"),
                func.count().label("total"),
            )
            .where(ActorProjectEdge.actor_id == actor_id)
            .where(ActorProjectEdge.edge_type.in_(["assigned", "completed", "joined"]))
        )
        row = result.first()
        if not row or row[1] == 0:
            return None
        return Decimal(str(round(row[0] / row[1], 4)))

    async def _actor_reuse_count(self, actor_id: uuid.UUID) -> int:
        """Number of projects the actor has been involved in more than once."""
        result = await self._session.execute(
            select(func.count(func.distinct(ActorProjectEdge.project_id))).where(
                ActorProjectEdge.actor_id == actor_id,
                ActorProjectEdge.status == "active",
            )
        )
        return result.scalar_one() or 0

    async def _actor_collaboration_breadth(self, actor_id: uuid.UUID) -> int:
        """Number of distinct projects."""
        result = await self._session.execute(
            select(func.count(func.distinct(ActorProjectEdge.project_id))).where(
                ActorProjectEdge.actor_id == actor_id
            )
        )
        return result.scalar_one() or 0

    async def _actor_coordination_load(self, actor_id: uuid.UUID) -> Decimal | None:
        """Simple load score = count of active edges."""
        result = await self._session.execute(
            select(func.count()).where(
                ActorProjectEdge.actor_id == actor_id,
                ActorProjectEdge.status == "active",
            )
        )
        count = result.scalar_one() or 0
        return Decimal(str(count)) if count > 0 else None

    async def _actor_public_benefit_score(self, actor_id: uuid.UUID) -> Decimal | None:
        """Ratio of public_benefit project edges to total."""
        result = await self._session.execute(
            select(
                func.count().filter(Project.project_type == "public_benefit").label("pb"),
                func.count().label("total"),
            )
            .select_from(ActorProjectEdge)
            .join(Project, Project.id == ActorProjectEdge.project_id)
            .where(ActorProjectEdge.actor_id == actor_id)
        )
        row = result.first()
        if not row or row[1] == 0:
            return None
        return Decimal(str(round(row[0] / row[1], 4)))

    async def _actor_review_reliability(self, actor_id: uuid.UUID) -> Decimal | None:
        """Placeholder — returns None until review_records are populated."""
        return None

    # ── Project Snapshot ────────────────────────────────────

    async def compute_project_snapshot(self, project_id: uuid.UUID) -> ProjectFeatureSnapshot:
        """Compute feature snapshot for a single project."""
        latest = await self._session.execute(
            select(func.coalesce(func.max(ProjectFeatureSnapshot.version), 0)).where(
                ProjectFeatureSnapshot.project_id == project_id
            )
        )
        next_version: int = latest.scalar_one() + 1

        task_count = await self._project_task_count(project_id)
        avg_ewu = await self._project_avg_ewu(project_id)
        max_ewu = await self._project_max_ewu(project_id)
        dep_density = await self._project_dependency_density(project_id)
        role_diversity = await self._project_role_diversity(project_id)
        complexity = await self._project_complexity(
            task_count, avg_ewu, dep_density, role_diversity
        )

        snapshot = ProjectFeatureSnapshot(
            project_id=project_id,
            version=next_version,
            task_count=task_count,
            avg_ewu=avg_ewu,
            max_ewu=max_ewu,
            dependency_density=dep_density,
            role_diversity_score=role_diversity,
            start_pattern=None,  # placeholder
            project_complexity_score=complexity,
            feature_json={
                "version": next_version,
                "computed_at": datetime.now(UTC).isoformat(),
            },
        )
        self._session.add(snapshot)

        # Update denormalized fields on project
        project = (
            await self._session.execute(select(Project).where(Project.id == project_id))
        ).scalar_one_or_none()
        if project:
            project.feature_snapshot_version = next_version  # type: ignore[assignment]
            project.last_feature_computed_at = datetime.now(UTC)  # type: ignore[assignment]
            project.task_count = task_count  # type: ignore[assignment]
            project.avg_ewu = avg_ewu  # type: ignore[assignment]
            project.max_ewu = max_ewu  # type: ignore[assignment]
            project.dependency_density = dep_density  # type: ignore[assignment]
            project.role_diversity_score = role_diversity  # type: ignore[assignment]
            project.project_complexity_score = complexity  # type: ignore[assignment]

        await self._session.flush()
        return snapshot

    async def _project_task_count(self, project_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(TaskCard)
            .join(WorkPackage, WorkPackage.id == TaskCard.work_package_id)
            .where(WorkPackage.project_id == project_id)
        )
        return result.scalar_one() or 0

    async def _project_avg_ewu(self, project_id: uuid.UUID) -> Decimal | None:
        result = await self._session.execute(
            select(func.avg(TaskCard.ewu))
            .join(WorkPackage, WorkPackage.id == TaskCard.work_package_id)
            .where(WorkPackage.project_id == project_id)
        )
        val = result.scalar_one()
        return Decimal(str(round(float(val), 2))) if val else None

    async def _project_max_ewu(self, project_id: uuid.UUID) -> Decimal | None:
        result = await self._session.execute(
            select(func.max(TaskCard.ewu))
            .join(WorkPackage, WorkPackage.id == TaskCard.work_package_id)
            .where(WorkPackage.project_id == project_id)
        )
        val = result.scalar_one()
        return Decimal(str(round(float(val), 2))) if val else None

    async def _project_dependency_density(self, project_id: uuid.UUID) -> Decimal | None:
        """Ratio of tasks with dependencies to total tasks."""
        result = await self._session.execute(
            select(
                func.count()
                .filter(TaskCard.dependency_task_ids_json.isnot(None))
                .label("with_deps"),
                func.count().label("total"),
            )
            .join(WorkPackage, WorkPackage.id == TaskCard.work_package_id)
            .where(WorkPackage.project_id == project_id)
        )
        row = result.first()
        if not row or row[1] == 0:
            return None
        return Decimal(str(round(row[0] / row[1], 4)))

    async def _project_role_diversity(self, project_id: uuid.UUID) -> Decimal | None:
        """Number of distinct roles needed / total tasks."""
        result = await self._session.execute(
            select(
                func.count(func.distinct(TaskCard.main_role)).label("roles"),
                func.count().label("total"),
            )
            .join(WorkPackage, WorkPackage.id == TaskCard.work_package_id)
            .where(WorkPackage.project_id == project_id)
        )
        row = result.first()
        if not row or row[1] == 0:
            return None
        return Decimal(str(round(row[0] / row[1], 4)))

    async def _project_complexity(
        self,
        task_count: int,
        avg_ewu: Decimal | None,
        dep_density: Decimal | None,
        role_diversity: Decimal | None,
    ) -> Decimal | None:
        """Simple rule-based complexity: weighted sum of normalized features."""
        if task_count == 0:
            return None
        score = Decimal("0")
        # Task count contributes 0-0.4
        score += min(Decimal(str(task_count / 20)), Decimal("1")) * Decimal("0.4")
        # Avg EWU contributes 0-0.3
        if avg_ewu:
            score += min(avg_ewu / Decimal("5"), Decimal("1")) * Decimal("0.3")
        # Dependency density contributes 0-0.15
        if dep_density:
            score += dep_density * Decimal("0.15")
        # Role diversity contributes 0-0.15
        if role_diversity:
            score += role_diversity * Decimal("0.15")
        return round(score, 4)
