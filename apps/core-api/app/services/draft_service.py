"""Draft service — business logic for draft CRUD."""

import uuid
from typing import Any

from shared_auth import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ForbiddenError, NotFoundError
from app.models.draft import Draft
from app.repositories.draft_repo import DraftRepository
from app.schemas.draft import (
    CreateDraftRequest,
    DraftResponse,
    UpdateDraftRequest,
)


class DraftService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = DraftRepository(session)

    async def create_draft(self, req: CreateDraftRequest, user: CurrentUser) -> DraftResponse:
        draft = Draft(
            actor_id=user.actor_id,
            draft_type=req.draft_type,
            source_channel=req.source_channel,
            collected_fields_json=req.collected_fields_json,
        )
        draft = await self._repo.create(draft)
        return DraftResponse.model_validate(draft)

    async def get_draft(self, draft_id: uuid.UUID, user: CurrentUser) -> DraftResponse:
        draft = await self._get_owned_draft(draft_id, user)
        return DraftResponse.model_validate(draft)

    async def list_my_drafts(self, user: CurrentUser) -> list[DraftResponse]:
        items = await self._repo.find_by_actor(user.actor_id)
        return [DraftResponse.model_validate(d) for d in items]

    async def update_draft(
        self, draft_id: uuid.UUID, req: UpdateDraftRequest, user: CurrentUser
    ) -> DraftResponse:
        draft = await self._get_owned_draft(draft_id, user)
        updates = req.model_dump(exclude_unset=True)
        # Deep merge collected_fields_json instead of overwriting
        if "collected_fields_json" in updates and updates["collected_fields_json"]:
            merged = dict(draft.collected_fields_json)
            merged.update(updates["collected_fields_json"])
            updates["collected_fields_json"] = merged
        draft = await self._repo.update_fields(draft, updates)
        return DraftResponse.model_validate(draft)

    async def delete_draft(self, draft_id: uuid.UUID, user: CurrentUser) -> None:
        draft = await self._get_owned_draft(draft_id, user)
        await self._repo.delete(draft)

    async def update_preflight_result(
        self,
        draft_id: uuid.UUID,
        user: CurrentUser,
        *,
        preflight_status: str,
        preflight_result_json: dict[str, Any] | None = None,
    ) -> DraftResponse:
        draft = await self._get_owned_draft(draft_id, user)
        updates: dict[str, object] = {"preflight_status": preflight_status}
        if preflight_result_json is not None:
            updates["preflight_result_json"] = preflight_result_json
        draft = await self._repo.update_fields(draft, updates)
        return DraftResponse.model_validate(draft)

    async def _get_owned_draft(self, draft_id: uuid.UUID, user: CurrentUser) -> Draft:
        draft = await self._repo.find_by_id(draft_id)
        if not draft:
            raise NotFoundError("Draft not found")
        if draft.actor_id != user.actor_id:
            raise ForbiddenError("Not your draft")
        return draft
