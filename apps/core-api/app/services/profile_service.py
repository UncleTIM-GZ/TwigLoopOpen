"""Profile service — get and update actor profile."""

from shared_auth import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.actor import Actor
from app.repositories.account_repo import AccountRepository
from app.repositories.actor_repo import ActorRepository
from app.schemas.user import AccountInfo, ActorInfo, MeResponse, UpdateProfileRequest


class ProfileService:
    def __init__(self, session: AsyncSession) -> None:
        self._account_repo = AccountRepository(session)
        self._actor_repo = ActorRepository(session)

    async def get_profile(self, user: CurrentUser) -> MeResponse:
        account = await self._account_repo.find_by_id(user.account_id)
        if not account:
            raise NotFoundError("Account not found")
        actor = await self._actor_repo.find_by_id(user.actor_id)
        if not actor:
            raise NotFoundError("Actor not found")
        return MeResponse(
            account=AccountInfo(account_id=account.id, email=account.email),
            actor=self._actor_to_info(actor),
        )

    async def update_profile(self, user: CurrentUser, req: UpdateProfileRequest) -> ActorInfo:
        actor = await self._actor_repo.find_by_id(user.actor_id)
        if not actor:
            raise NotFoundError("Actor not found")

        updates = req.model_dump(exclude_unset=True)
        # Map schema fields to model JSONB columns
        if "skills" in updates:
            updates["skills_json"] = updates.pop("skills")
        if "interested_project_types" in updates:
            updates["interested_project_types_json"] = updates.pop("interested_project_types")
        # Whitelist: only allow safe fields to be updated
        allowed = {
            "display_name",
            "bio",
            "availability",
            "skills_json",
            "interested_project_types_json",
        }
        updates = {k: v for k, v in updates.items() if k in allowed}
        actor = await self._actor_repo.update_fields(actor, updates)
        return self._actor_to_info(actor)

    @staticmethod
    def _actor_to_info(actor: Actor) -> ActorInfo:
        return ActorInfo(
            actor_id=actor.id,
            display_name=actor.display_name,
            actor_type=actor.actor_type,
            bio=actor.bio,
            availability=actor.availability,
            skills=actor.skills_json if isinstance(actor.skills_json, list) else None,
            interested_project_types=(
                actor.interested_project_types_json
                if isinstance(actor.interested_project_types_json, list)
                else None
            ),
            is_founder=actor.is_founder,
            is_collaborator=actor.is_collaborator,
            is_reviewer=actor.is_reviewer,
            is_sponsor=actor.is_sponsor,
            profile_status=actor.profile_status,
            level=actor.level,
        )
