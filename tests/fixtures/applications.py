"""Application fixtures — normal and over-capacity scenarios."""

from datetime import UTC, datetime

import pytest

from app.models.application import ProjectApplication


def _make_application(
    *,
    project_id,
    actor_id,
    seat_preference: str = "growth",
    intended_role: str = "developer",
    status: str = "submitted",
) -> ProjectApplication:
    """Build a ProjectApplication instance without persisting."""
    app = ProjectApplication(
        project_id=project_id,
        actor_id=actor_id,
        seat_preference=seat_preference,
        intended_role=intended_role,
        motivation="I want to contribute",
        availability="10h/week",
        status=status,
    )
    now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
    app.created_at = now
    app.updated_at = now
    return app


# ── Normal application ──────────────────────────────────────────────────


@pytest.fixture
async def normal_application(
    session, general_project, collaborator_actor
) -> ProjectApplication:
    app = _make_application(
        project_id=general_project.id,
        actor_id=collaborator_actor.id,
    )
    session.add(app)
    await session.flush()
    return app


# ── Project with 30 applications (at limit) ─────────────────────────────


@pytest.fixture
async def project_with_30_apps(session, founder_actor, general_project):
    """Return (project, [30 applications]).

    Creates 30 unique collaborator accounts/actors and their applications.
    """
    from app.models.account import Account
    from app.models.actor import Actor

    apps = []
    now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)

    for i in range(30):
        account = Account(
            email=f"applicant-{i}@twigloop.test",
            password_hash="$2b$12$fakehash",
            auth_method="password",
            registration_source="web",
            status="active",
        )
        account.created_at = now
        account.updated_at = now
        session.add(account)
        await session.flush()

        actor = Actor(
            account_id=account.id,
            display_name=f"Applicant {i}",
            actor_type="human",
            is_collaborator=True,
            profile_status="profile_complete",
            level="L0",
        )
        actor.created_at = now
        actor.updated_at = now
        session.add(actor)
        await session.flush()

        application = _make_application(
            project_id=general_project.id,
            actor_id=actor.id,
            intended_role=f"role-{i}",
        )
        session.add(application)
        apps.append(application)

    await session.flush()
    return general_project, apps
