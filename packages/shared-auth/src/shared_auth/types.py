"""Auth type definitions."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class TokenPayload(BaseModel):
    """JWT token payload."""

    account_id: uuid.UUID
    actor_id: uuid.UUID
    roles: list[str]
    exp: datetime
    token_type: str  # "access" or "refresh"
    jti: str  # unique token ID for refresh token revocation


class CurrentUser(BaseModel):
    """Injected user context from JWT."""

    account_id: uuid.UUID
    actor_id: uuid.UUID
    roles: list[str]
