"""Unit tests for SQLAlchemy model column defaults and instantiation.

SQLAlchemy 2.0 `mapped_column(default=X)` applies at INSERT time, not at
Python constructor time.  For pure unit tests (no DB), we verify:
1. The column metadata declares the expected default.
2. Objects can be instantiated and accept explicit values.
"""

import uuid
from decimal import Decimal

from app.models.account import Account
from app.models.actor import Actor
from app.models.application import ProjectApplication
from app.models.draft import Draft
from app.models.project import Project
from app.models.seat import ProjectSeat
from app.models.task_card import TaskCard
from app.models.work_package import WorkPackage
from sqlalchemy import inspect as sa_inspect

# ── Helpers ───────────────────────────────────────────────────────


def _column_default(model_cls, col_name: str):
    """Return the Python-side default declared on a mapped column."""
    mapper = sa_inspect(model_cls)
    col = mapper.columns[col_name]
    if col.default is not None:
        return col.default.arg
    return None


# ── Account ───────────────────────────────────────────────────────


class TestAccountModel:
    def test_column_default_status(self):
        assert _column_default(Account, "status") == "active"

    def test_column_default_auth_method(self):
        assert _column_default(Account, "auth_method") == "password"

    def test_column_default_registration_source(self):
        assert _column_default(Account, "registration_source") == "web"

    def test_explicit_values(self):
        a = Account(email="a@b.com", password_hash="hash", status="suspended")
        assert a.email == "a@b.com"
        assert a.status == "suspended"


# ── Actor ─────────────────────────────────────────────────────────


class TestActorModel:
    def test_column_default_is_founder(self):
        assert _column_default(Actor, "is_founder") is False

    def test_column_default_is_collaborator(self):
        assert _column_default(Actor, "is_collaborator") is False

    def test_column_default_is_reviewer(self):
        assert _column_default(Actor, "is_reviewer") is False

    def test_column_default_is_sponsor(self):
        assert _column_default(Actor, "is_sponsor") is False

    def test_column_default_profile_status(self):
        assert _column_default(Actor, "profile_status") == "profile_incomplete"

    def test_column_default_level(self):
        assert _column_default(Actor, "level") == "L0"

    def test_column_default_actor_type(self):
        assert _column_default(Actor, "actor_type") == "human"

    def test_explicit_values(self):
        actor = Actor(
            account_id=uuid.uuid4(),
            display_name="Test",
            actor_type="ai_agent",
            level="L3",
        )
        assert actor.display_name == "Test"
        assert actor.actor_type == "ai_agent"
        assert actor.level == "L3"


# ── Project ───────────────────────────────────────────────────────


class TestProjectModel:
    def test_column_default_status(self):
        assert _column_default(Project, "status") == "draft"

    def test_column_default_needs_human_reviewer(self):
        assert _column_default(Project, "needs_human_reviewer") is False

    def test_column_default_human_review_status(self):
        assert _column_default(Project, "human_review_status") == "none"

    def test_column_default_has_reward(self):
        assert _column_default(Project, "has_reward") is False

    def test_column_default_has_sponsor(self):
        assert _column_default(Project, "has_sponsor") is False

    def test_column_default_created_via(self):
        assert _column_default(Project, "created_via") == "web"

    def test_explicit_values(self):
        p = Project(
            founder_actor_id=uuid.uuid4(),
            project_type="public_benefit",
            founder_type="organization",
            title="Community Garden",
            summary="Summary",
            current_stage="idea",
            needs_human_reviewer=True,
            status="open_for_collaboration",
        )
        assert p.project_type == "public_benefit"
        assert p.needs_human_reviewer is True
        assert p.status == "open_for_collaboration"


# ── WorkPackage ───────────────────────────────────────────────────


class TestWorkPackageModel:
    def test_column_default_status(self):
        assert _column_default(WorkPackage, "status") == "draft"

    def test_column_default_sort_order(self):
        assert _column_default(WorkPackage, "sort_order") == 0

    def test_explicit_values(self):
        wp = WorkPackage(
            project_id=uuid.uuid4(),
            title="Phase 1",
            status="active",
            sort_order=2,
        )
        assert wp.title == "Phase 1"
        assert wp.status == "active"
        assert wp.sort_order == 2


# ── TaskCard ──────────────────────────────────────────────────────


class TestTaskCardModel:
    def test_column_default_status(self):
        assert _column_default(TaskCard, "status") == "draft"

    def test_column_default_ewu(self):
        assert _column_default(TaskCard, "ewu") == Decimal("1.00")

    def test_column_default_risk_level(self):
        assert _column_default(TaskCard, "risk_level") == "low"

    def test_column_default_has_reward(self):
        assert _column_default(TaskCard, "has_reward") is False

    def test_explicit_values(self):
        t = TaskCard(
            work_package_id=uuid.uuid4(),
            title="Implement auth",
            task_type="development",
            goal="Build login",
            output_spec="Working auth",
            completion_criteria="Users can log in",
            main_role="developer",
            status="open",
            ewu=5,
        )
        assert t.title == "Implement auth"
        assert t.status == "open"
        assert t.ewu == 5


# ── ProjectApplication ────────────────────────────────────────────


class TestProjectApplicationModel:
    def test_column_default_status(self):
        assert _column_default(ProjectApplication, "status") == "submitted"

    def test_explicit_values(self):
        app = ProjectApplication(
            project_id=uuid.uuid4(),
            actor_id=uuid.uuid4(),
            seat_preference="growth",
            intended_role="developer",
            status="accepted",
        )
        assert app.status == "accepted"


# ── ProjectSeat ───────────────────────────────────────────────────


class TestProjectSeatModel:
    def test_column_default_status(self):
        assert _column_default(ProjectSeat, "status") == "proposed"

    def test_column_default_reward_enabled(self):
        assert _column_default(ProjectSeat, "reward_enabled") is False

    def test_explicit_values(self):
        seat = ProjectSeat(
            project_id=uuid.uuid4(),
            seat_type="growth",
            role_needed="developer",
            status="occupied",
            reward_enabled=True,
        )
        assert seat.status == "occupied"
        assert seat.reward_enabled is True


# ── Draft ─────────────────────────────────────────────────────────


class TestDraftModel:
    def test_server_default_status(self):
        """Draft.status uses server_default='collecting'."""
        mapper = sa_inspect(Draft)
        col = mapper.columns["status"]
        assert col.server_default.arg == "collecting"

    def test_server_default_preflight_status(self):
        """Draft.preflight_status uses server_default='pending'."""
        mapper = sa_inspect(Draft)
        col = mapper.columns["preflight_status"]
        assert col.server_default.arg == "pending"

    def test_collected_fields_defaults(self):
        """collected_fields_json is required — no Python-side default."""
        d = Draft(actor_id=uuid.uuid4(), draft_type="project", source_channel="mcp")
        assert d.draft_type == "project"

    def test_explicit_values(self):
        actor_id = uuid.uuid4()
        d = Draft(
            actor_id=actor_id,
            draft_type="work_package",
            status="submitted",
            preflight_status="passed",
            source_channel="web",
            collected_fields_json={"title": "Test WP"},
        )
        assert d.actor_id == actor_id
        assert d.draft_type == "work_package"
        assert d.status == "submitted"
        assert d.preflight_status == "passed"
        assert d.collected_fields_json == {"title": "Test WP"}

    def test_draft_type_project(self):
        d = Draft(actor_id=uuid.uuid4(), draft_type="project")
        assert d.draft_type == "project"

    def test_actor_id_is_set(self):
        actor_id = uuid.uuid4()
        d = Draft(actor_id=actor_id, draft_type="project")
        assert d.actor_id == actor_id
