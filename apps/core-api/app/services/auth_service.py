"""Authentication service — register and login logic."""

import jwt as pyjwt
from shared_auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from shared_events import Subjects, publish_event
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, UnauthorizedError
from app.models.account import Account
from app.models.actor import Actor
from app.repositories.account_repo import AccountRepository
from app.repositories.actor_repo import ActorRepository
from app.schemas.auth import AuthResponse, LoginRequest, RefreshTokenRequest, RegisterRequest
from app.services.event_write_service import EventWriteService


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._account_repo = AccountRepository(session)
        self._actor_repo = ActorRepository(session)
        self._events = EventWriteService(session)

    async def register(self, req: RegisterRequest) -> AuthResponse:
        existing = await self._account_repo.find_by_email(req.email)
        if existing:
            raise ConflictError("Email already registered")

        account = Account(
            email=req.email,
            password_hash=hash_password(req.password),
            auth_method="password",
            registration_source="web",
        )
        account = await self._account_repo.create(account)

        is_founder = req.entry_intent in ("founder", "both")
        is_collaborator = req.entry_intent in ("collaborator", "both")

        actor = Actor(
            account_id=account.id,
            display_name=req.display_name,
            is_founder=is_founder,
            is_collaborator=is_collaborator,
        )
        actor = await self._actor_repo.create(actor)

        await publish_event(
            Subjects.ACCOUNT_REGISTERED,
            {"account_id": str(account.id), "actor_id": str(actor.id)},
            actor_id=actor.id,
        )

        try:
            await self._events.record_domain_event(
                "account_registered",
                "account",
                account.id,
                payload={"email": account.email},
            )
            await self._events.record_domain_event(
                "actor_profile_updated",
                "actor",
                actor.id,
                actor_id=actor.id,
            )
        except Exception:
            pass  # Event write failure should not block business logic during transition

        roles = self._build_roles(actor)
        return AuthResponse(
            account_id=account.id,
            actor_id=actor.id,
            access_token=create_access_token(account.id, actor.id, roles),
            refresh_token=create_refresh_token(account.id, actor.id, roles),
        )

    async def login(self, req: LoginRequest) -> AuthResponse:
        account = await self._account_repo.find_by_email(req.email)
        if not account:
            raise UnauthorizedError("Invalid email or password")

        if not verify_password(req.password, account.password_hash):
            raise UnauthorizedError("Invalid email or password")

        actor = await self._actor_repo.find_by_account_id(account.id)
        if not actor:
            raise UnauthorizedError("No actor profile found")

        roles = self._build_roles(actor)
        return AuthResponse(
            account_id=account.id,
            actor_id=actor.id,
            access_token=create_access_token(account.id, actor.id, roles),
            refresh_token=create_refresh_token(account.id, actor.id, roles),
        )

    async def refresh(self, req: RefreshTokenRequest) -> AuthResponse:
        try:
            payload = decode_token(req.refresh_token)
        except pyjwt.InvalidTokenError as err:
            raise UnauthorizedError("Invalid or expired refresh token") from err

        if payload.token_type != "refresh":
            raise UnauthorizedError("Invalid token type")

        account = await self._account_repo.find_by_id(payload.account_id)
        if not account:
            raise UnauthorizedError("Account not found")

        actor = await self._actor_repo.find_by_account_id(account.id)
        if not actor:
            raise UnauthorizedError("No actor profile found")

        roles = self._build_roles(actor)
        return AuthResponse(
            account_id=account.id,
            actor_id=actor.id,
            access_token=create_access_token(account.id, actor.id, roles),
            refresh_token=create_refresh_token(account.id, actor.id, roles),
        )

    @staticmethod
    def _build_roles(actor: Actor) -> list[str]:
        roles: list[str] = []
        if actor.is_founder:
            roles.append("founder")
        if actor.is_collaborator:
            roles.append("collaborator")
        if actor.is_reviewer:
            roles.append("reviewer")
        if actor.is_sponsor:
            roles.append("sponsor")
        return roles
