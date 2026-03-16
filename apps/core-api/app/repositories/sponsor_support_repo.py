"""Sponsor support repository — data access for sponsor_supports table."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sponsor_support import SponsorSupport


class SponsorSupportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, support: SponsorSupport) -> SponsorSupport:
        self._session.add(support)
        await self._session.flush()
        return support

    async def find_by_sponsor(self, sponsor_actor_id: uuid.UUID) -> list[SponsorSupport]:
        stmt = (
            select(SponsorSupport)
            .where(SponsorSupport.sponsor_actor_id == sponsor_actor_id)
            .order_by(SponsorSupport.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_project(self, project_id: uuid.UUID) -> list[SponsorSupport]:
        stmt = (
            select(SponsorSupport)
            .where(SponsorSupport.project_id == project_id)
            .order_by(SponsorSupport.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
