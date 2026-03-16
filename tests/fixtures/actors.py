"""Actor and account fixtures for test scenarios.

Roles:
- founder_account / founder_actor:  Person A who initiates projects
- new_founder_account / new_founder_actor:  Second founder for capacity tests
- collaborator_actor:  Person B who applies to projects
- reviewer_actor:  Public-benefit project reviewer
- sponsor_actor:  Sponsor who funds projects
- public_benefit_user:  Founder who creates public-benefit projects
- mcp_user:  Actor with both founder+collaborator roles (MCP client)
"""

import uuid
from datetime import UTC, datetime

import pytest

from app.models.account import Account
from app.models.actor import Actor


def _make_account(
    *,
    account_id: uuid.UUID | None = None,
    email: str = "test@example.com",
    password_hash: str = "$2b$12$fakehash",
) -> Account:
    """Build an Account instance without persisting."""
    account = Account(
        email=email,
        password_hash=password_hash,
        auth_method="password",
        registration_source="web",
        status="active",
    )
    if account_id:
        account.id = account_id
    now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
    account.created_at = now
    account.updated_at = now
    return account


def _make_actor(
    *,
    actor_id: uuid.UUID | None = None,
    account_id: uuid.UUID,
    display_name: str = "Test User",
    is_founder: bool = False,
    is_collaborator: bool = False,
    is_reviewer: bool = False,
    is_sponsor: bool = False,
) -> Actor:
    """Build an Actor instance without persisting."""
    actor = Actor(
        account_id=account_id,
        display_name=display_name,
        actor_type="human",
        is_founder=is_founder,
        is_collaborator=is_collaborator,
        is_reviewer=is_reviewer,
        is_sponsor=is_sponsor,
        profile_status="profile_complete",
        level="L0",
    )
    if actor_id:
        actor.id = actor_id
    now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
    actor.created_at = now
    actor.updated_at = now
    return actor


# ── Founder (Person A) ──────────────────────────────────────────────────


@pytest.fixture
async def founder_account(session) -> Account:
    account = _make_account(email="founder@twigloop.test")
    session.add(account)
    await session.flush()
    return account


@pytest.fixture
async def founder_actor(session, founder_account) -> Actor:
    actor = _make_actor(
        account_id=founder_account.id,
        display_name="Founder Alice",
        is_founder=True,
    )
    session.add(actor)
    await session.flush()
    return actor


# ── New Founder (for capacity tests) ─────────────────────────────────────


@pytest.fixture
async def new_founder_account(session) -> Account:
    account = _make_account(email="new-founder@twigloop.test")
    session.add(account)
    await session.flush()
    return account


@pytest.fixture
async def new_founder_actor(session, new_founder_account) -> Actor:
    actor = _make_actor(
        account_id=new_founder_account.id,
        display_name="Founder Bob",
        is_founder=True,
    )
    session.add(actor)
    await session.flush()
    return actor


# ── Collaborator (Person B) ─────────────────────────────────────────────


@pytest.fixture
async def collaborator_account(session) -> Account:
    account = _make_account(email="collaborator@twigloop.test")
    session.add(account)
    await session.flush()
    return account


@pytest.fixture
async def collaborator_actor(session, collaborator_account) -> Actor:
    actor = _make_actor(
        account_id=collaborator_account.id,
        display_name="Collaborator Charlie",
        is_collaborator=True,
    )
    session.add(actor)
    await session.flush()
    return actor


# ── Reviewer ──────────────────────────────────────────────────────────────


@pytest.fixture
async def reviewer_account(session) -> Account:
    account = _make_account(email="reviewer@twigloop.test")
    session.add(account)
    await session.flush()
    return account


@pytest.fixture
async def reviewer_actor(session, reviewer_account) -> Actor:
    actor = _make_actor(
        account_id=reviewer_account.id,
        display_name="Reviewer Diana",
        is_reviewer=True,
    )
    session.add(actor)
    await session.flush()
    return actor


# ── Sponsor ──────────────────────────────────────────────────────────────


@pytest.fixture
async def sponsor_account(session) -> Account:
    account = _make_account(email="sponsor@twigloop.test")
    session.add(account)
    await session.flush()
    return account


@pytest.fixture
async def sponsor_actor(session, sponsor_account) -> Actor:
    actor = _make_actor(
        account_id=sponsor_account.id,
        display_name="Sponsor Eve",
        is_sponsor=True,
    )
    session.add(actor)
    await session.flush()
    return actor


# ── Public Benefit User (founder for org) ────────────────────────────────


@pytest.fixture
async def public_benefit_account(session) -> Account:
    account = _make_account(email="pb-founder@twigloop.test")
    session.add(account)
    await session.flush()
    return account


@pytest.fixture
async def public_benefit_user(session, public_benefit_account) -> Actor:
    actor = _make_actor(
        account_id=public_benefit_account.id,
        display_name="PB Founder Frank",
        is_founder=True,
    )
    session.add(actor)
    await session.flush()
    return actor


# ── MCP User (both founder + collaborator) ───────────────────────────────


@pytest.fixture
async def mcp_account(session) -> Account:
    account = _make_account(email="mcp@twigloop.test")
    session.add(account)
    await session.flush()
    return account


@pytest.fixture
async def mcp_user(session, mcp_account) -> Actor:
    actor = _make_actor(
        account_id=mcp_account.id,
        display_name="MCP Grace",
        is_founder=True,
        is_collaborator=True,
    )
    session.add(actor)
    await session.flush()
    return actor
