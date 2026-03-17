"""Brief service — persists and retrieves agent-generated briefs.

Handles MatchingBrief and ReviewBrief as typed AgentBrief records.
Agent generates → service persists → API/frontend reads.
"""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_brief import AgentBrief
from app.repositories.agent_brief_repo import AgentBriefRepository

logger = logging.getLogger(__name__)


class BriefService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = AgentBriefRepository(session)

    async def save_brief(
        self,
        *,
        task_id: uuid.UUID,
        brief_type: str,
        brief_source: str,
        content: dict,
        actor_id: uuid.UUID | None = None,
        delegation_id: str | None = None,
        trace_id: str | None = None,
    ) -> AgentBrief:
        """Save a new brief, superseding any existing active brief of same type."""
        # Get current version
        existing = await self._repo.find_latest(task_id, brief_type)
        new_version = (existing.brief_version + 1) if existing else 1

        # Supersede existing
        if existing:
            await self._repo.supersede_existing(task_id, brief_type)

        brief = AgentBrief(
            task_id=task_id,
            brief_type=brief_type,
            brief_source=brief_source,
            brief_version=new_version,
            status="active",
            content_json=content,
            actor_id=actor_id,
            delegation_id=delegation_id,
            trace_id=trace_id,
        )
        brief = await self._repo.create(brief)

        logger.info(
            "brief_saved",
            extra={
                "brief_id": str(brief.id),
                "task_id": str(task_id),
                "brief_type": brief_type,
                "brief_source": brief_source,
                "brief_version": new_version,
                "trace_id": trace_id,
            },
        )
        return brief

    async def get_latest(self, task_id: uuid.UUID, brief_type: str) -> AgentBrief | None:
        return await self._repo.find_latest(task_id, brief_type)

    async def get_history(self, task_id: uuid.UUID, brief_type: str) -> list[AgentBrief]:
        return await self._repo.find_all_by_task(task_id, brief_type)
