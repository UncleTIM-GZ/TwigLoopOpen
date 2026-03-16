"""Account repository — data access for accounts table."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class AccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, account_id: uuid.UUID) -> Account | None:
        stmt = select(Account).where(Account.id == account_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> Account | None:
        stmt = select(Account).where(Account.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, account: Account) -> Account:
        self._session.add(account)
        await self._session.flush()
        return account
