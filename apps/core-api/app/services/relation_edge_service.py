"""Relation edge service — writes relation edges between actors and projects."""

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.edges import ActorActorEdge, ActorProjectEdge
from app.repositories.edge_repo import ActorActorEdgeRepository, ActorProjectEdgeRepository


class RelationEdgeService:
    """Writes relation edges. Shares session with caller."""

    def __init__(self, session: AsyncSession) -> None:
        self._ap_repo = ActorProjectEdgeRepository(session)
        self._aa_repo = ActorActorEdgeRepository(session)

    async def create_actor_project_edge(
        self,
        actor_id: uuid.UUID,
        project_id: uuid.UUID,
        edge_type: str,
        *,
        source_event_id: uuid.UUID | None = None,
        weight: Decimal = Decimal("1.0"),
    ) -> ActorProjectEdge:
        edge = ActorProjectEdge(
            actor_id=actor_id,
            project_id=project_id,
            edge_type=edge_type,
            weight=weight,
            source_event_id=source_event_id,
        )
        return await self._ap_repo.create(edge)

    async def create_actor_actor_edge(
        self,
        actor_a_id: uuid.UUID,
        actor_b_id: uuid.UUID,
        edge_type: str,
        *,
        project_id: uuid.UUID | None = None,
        task_id: uuid.UUID | None = None,
        source_event_id: uuid.UUID | None = None,
        weight: Decimal = Decimal("1.0"),
    ) -> ActorActorEdge:
        edge = ActorActorEdge(
            actor_a_id=actor_a_id,
            actor_b_id=actor_b_id,
            edge_type=edge_type,
            project_id=project_id,
            task_id=task_id,
            weight=weight,
            source_event_id=source_event_id,
        )
        return await self._aa_repo.create(edge)
