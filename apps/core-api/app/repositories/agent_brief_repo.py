"""AgentBrief repository."""

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_brief import AgentBrief


class AgentBriefRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, brief: AgentBrief) -> AgentBrief:
        self._session.add(brief)
        await self._session.flush()
        return brief

    async def find_latest(self, task_id: uuid.UUID, brief_type: str) -> AgentBrief | None:
        stmt = (
            select(AgentBrief)
            .where(
                AgentBrief.task_id == task_id,
                AgentBrief.brief_type == brief_type,
                AgentBrief.status == "active",
            )
            .order_by(AgentBrief.brief_version.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all_by_task(self, task_id: uuid.UUID, brief_type: str) -> list[AgentBrief]:
        stmt = (
            select(AgentBrief)
            .where(
                AgentBrief.task_id == task_id,
                AgentBrief.brief_type == brief_type,
            )
            .order_by(AgentBrief.brief_version.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def supersede_existing(self, task_id: uuid.UUID, brief_type: str) -> None:
        stmt = (
            update(AgentBrief)
            .where(
                AgentBrief.task_id == task_id,
                AgentBrief.brief_type == brief_type,
                AgentBrief.status == "active",
            )
            .values(status="superseded")
        )
        await self._session.execute(stmt)
