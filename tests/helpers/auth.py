"""Auth helpers — create test tokens and users."""

import uuid

from shared_auth import CurrentUser, create_access_token


def get_test_token(
    account_id: uuid.UUID,
    actor_id: uuid.UUID,
    roles: tuple[str, ...] = ("founder",),
) -> str:
    """Create a valid JWT access token for test requests."""
    return create_access_token(account_id, actor_id, list(roles))


def make_current_user(
    account_id: uuid.UUID,
    actor_id: uuid.UUID,
    roles: tuple[str, ...] = ("founder",),
) -> CurrentUser:
    """Build a CurrentUser object for direct service-layer testing."""
    return CurrentUser(
        account_id=account_id,
        actor_id=actor_id,
        roles=list(roles),
    )


def auth_header(
    account_id: uuid.UUID,
    actor_id: uuid.UUID,
    roles: tuple[str, ...] = ("founder",),
) -> dict[str, str]:
    """Return an Authorization header dict for httpx test client."""
    token = get_test_token(account_id, actor_id, roles)
    return {"Authorization": f"Bearer {token}"}
