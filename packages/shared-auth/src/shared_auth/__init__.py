"""Shared authentication and authorization for Twig Loop."""

from shared_auth.deps import get_current_user, require_role
from shared_auth.jwt import create_access_token, create_refresh_token, decode_token
from shared_auth.password import hash_password, verify_password
from shared_auth.rbac import Role
from shared_auth.types import CurrentUser, TokenPayload

__all__ = [
    "CurrentUser",
    "Role",
    "TokenPayload",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "get_current_user",
    "hash_password",
    "require_role",
    "verify_password",
]
