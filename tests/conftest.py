"""Root conftest — shared fixtures and DB setup for all tests.

Uses SQLite in-memory for unit tests (fast, no external deps).
Integration tests that need PostgreSQL-specific features should use a
separate conftest with a real database URL.
"""

# Register fixture modules so pytest discovers them globally
pytest_plugins = [
    "tests.fixtures.actors",
    "tests.fixtures.projects",
    "tests.fixtures.tasks",
    "tests.fixtures.applications",
]

import asyncio
import os
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import Text, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.types import JSON

from app.models.base import Base

# ---------------------------------------------------------------------------
# Override env vars BEFORE any shared_config/shared_auth import
# ---------------------------------------------------------------------------
os.environ.setdefault("JWT_SECRET", "test-secret-key-must-be-at-least-32-chars-long")
# Use a dummy PostgreSQL URL so app.db.session module can create its engine
# at import time (pool_size/max_overflow require a poolable dialect).
# We never actually connect via this engine — get_session is overridden.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/test_twigloop",
)
os.environ.setdefault("NATS_URL", "nats://localhost:4222")
os.environ.setdefault("ENVIRONMENT", "test")

# ---------------------------------------------------------------------------
# Event loop (session-scoped so engine can be reused)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# SQLite compatibility: compile PostgreSQL types to SQLite equivalents
# ---------------------------------------------------------------------------

_pg_types_patched = False


def _patch_pg_types_for_sqlite():
    """Register compile hooks so JSONB and UUID render as SQLite types."""
    global _pg_types_patched  # noqa: PLW0603
    if _pg_types_patched:
        return
    _pg_types_patched = True

    from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID  # noqa: N811

    from sqlalchemy.ext.compiler import compiles

    @compiles(JSONB, "sqlite")  # type: ignore[misc]
    def _compile_jsonb_sqlite(element, compiler, **kw):  # type: ignore[no-untyped-def]
        return "TEXT"

    @compiles(PG_UUID, "sqlite")  # type: ignore[misc]
    def _compile_uuid_sqlite(element, compiler, **kw):  # type: ignore[no-untyped-def]
        return "CHAR(32)"


_patch_pg_types_for_sqlite()


# ---------------------------------------------------------------------------
# Async database session fixture
# ---------------------------------------------------------------------------


@pytest.fixture
async def engine():
    """Create an in-memory SQLite async engine with all tables."""
    eng = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide an async session bound to the in-memory test database."""
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as sess:
        yield sess


# ---------------------------------------------------------------------------
# Mock NATS publish_event so tests never hit a real broker
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def mock_nats_publish():
    """Globally mock publish_event to prevent NATS connections in tests."""
    with patch("shared_events.publisher.publish_event", new_callable=AsyncMock) as mock_pub:
        # Also patch the convenience import used by services
        with patch("shared_events.publish_event", new_callable=AsyncMock) as mock_pub2:
            yield mock_pub2


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """Reset in-memory rate limiters between tests."""
    from app.rate_limit import auth_rate_limit, public_rate_limit

    public_rate_limit.reset()
    auth_rate_limit.reset()
    yield
    public_rate_limit.reset()
    auth_rate_limit.reset()


# ---------------------------------------------------------------------------
# FastAPI test client (for integration tests)
# ---------------------------------------------------------------------------


@pytest.fixture
async def client(engine, session):
    """Provide an httpx AsyncClient wired to the test database.

    Patches app.db.session module-level objects so integration tests
    use our in-memory SQLite engine instead of PostgreSQL.
    """
    import importlib
    import sys

    import app.db.session as session_mod

    # Replace engine and factory before any route handler uses them
    test_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session_mod.engine = engine
    session_mod.async_session_factory = test_factory

    # Also patch modules that import async_session_factory by name
    import app.api.v1.webhooks as webhooks_mod

    webhooks_mod.async_session_factory = test_factory  # type: ignore[attr-defined]

    from httpx import ASGITransport, AsyncClient

    from app.main import app

    # Override get_session dependency to yield our specific test session
    async def _override_get_session():  # type: ignore[no-untyped-def]
        yield session

    app.dependency_overrides[session_mod.get_session] = _override_get_session

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Convenience: pre-built UUIDs for deterministic test data
# ---------------------------------------------------------------------------


@pytest.fixture
def fixed_uuids():
    """Return a dict of deterministic UUIDs for test data."""
    return {
        "account_a": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "actor_a": uuid.UUID("00000000-0000-0000-0000-000000000002"),
        "account_b": uuid.UUID("00000000-0000-0000-0000-000000000003"),
        "actor_b": uuid.UUID("00000000-0000-0000-0000-000000000004"),
        "account_c": uuid.UUID("00000000-0000-0000-0000-000000000005"),
        "actor_c": uuid.UUID("00000000-0000-0000-0000-000000000006"),
        "project_1": uuid.UUID("00000000-0000-0000-0000-000000000010"),
        "wp_1": uuid.UUID("00000000-0000-0000-0000-000000000020"),
        "task_1": uuid.UUID("00000000-0000-0000-0000-000000000030"),
        "app_1": uuid.UUID("00000000-0000-0000-0000-000000000040"),
    }


@pytest.fixture
def now():
    """Return a fixed 'now' timestamp for test data."""
    return datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
