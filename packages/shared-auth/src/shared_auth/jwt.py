"""JWT token creation and verification."""

import uuid
from datetime import UTC, datetime, timedelta

import jwt
from shared_config import JWTSettings

from shared_auth.types import CurrentUser, TokenPayload

_settings = JWTSettings()


def create_access_token(account_id: uuid.UUID, actor_id: uuid.UUID, roles: list[str]) -> str:
    """Create a short-lived access token."""
    now = datetime.now(UTC)
    payload = {
        "account_id": str(account_id),
        "actor_id": str(actor_id),
        "roles": roles,
        "token_type": "access",
        "jti": str(uuid.uuid4()),
        "exp": now + timedelta(minutes=_settings.jwt_access_token_expire_minutes),
        "iat": now,
    }
    return jwt.encode(payload, _settings.jwt_secret, algorithm=_settings.jwt_algorithm)


def create_refresh_token(account_id: uuid.UUID, actor_id: uuid.UUID, roles: list[str]) -> str:
    """Create a long-lived refresh token."""
    now = datetime.now(UTC)
    payload = {
        "account_id": str(account_id),
        "actor_id": str(actor_id),
        "roles": roles,
        "token_type": "refresh",
        "jti": str(uuid.uuid4()),
        "exp": now + timedelta(days=_settings.jwt_refresh_token_expire_days),
        "iat": now,
    }
    return jwt.encode(payload, _settings.jwt_secret, algorithm=_settings.jwt_algorithm)


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token. Raises jwt.InvalidTokenError on failure."""
    data = jwt.decode(token, _settings.jwt_secret, algorithms=[_settings.jwt_algorithm])
    try:
        return TokenPayload(
            account_id=uuid.UUID(data["account_id"]),
            actor_id=uuid.UUID(data["actor_id"]),
            roles=data["roles"],
            exp=datetime.fromtimestamp(data["exp"], tz=UTC),
            token_type=data["token_type"],
            jti=data["jti"],
        )
    except (KeyError, ValueError) as err:
        raise jwt.InvalidTokenError("Malformed token payload") from err


def token_to_current_user(payload: TokenPayload) -> CurrentUser:
    """Extract CurrentUser from a validated token payload."""
    return CurrentUser(
        account_id=payload.account_id,
        actor_id=payload.actor_id,
        roles=payload.roles,
    )
