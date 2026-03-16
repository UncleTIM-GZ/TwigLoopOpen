"""Tests for quota preflight logic — draft parsing / validation.

Tests the QuotaPreflightService.check_project_quota() method's draft-parsing
logic (work package count, tasks-per-WP, total tasks, EWU-per-task).
DB-dependent checks (active projects, open seats, active tasks) are mocked.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from app.services.quota_preflight_service import QuotaPreflightService
from sqlalchemy.ext.asyncio import AsyncSession

# ── Helpers ───────────────────────────────────────────────────────


def _make_wp(title: str = "WP", tasks: list | None = None) -> dict:
    return {"title": title, "tasks": tasks or []}


def _make_task(title: str = "Task", ewu: int = 1) -> dict:
    return {"title": title, "ewu": ewu}


ACTOR_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture
def service(session: AsyncSession) -> QuotaPreflightService:
    return QuotaPreflightService(session)


async def _check(service: QuotaPreflightService, wps: list) -> list:
    """Run check_project_quota with DB counters mocked to zero."""
    with (
        patch.object(service, "_count_active_projects", new_callable=AsyncMock, return_value=0),
        patch.object(service, "_count_open_seats", new_callable=AsyncMock, return_value=0),
        patch.object(service, "_count_active_tasks", new_callable=AsyncMock, return_value=0),
    ):
        return await service.check_project_quota({"work_packages": wps}, ACTOR_ID)


# ── Work package count ────────────────────────────────────────────


class TestWorkPackageCount:
    async def test_zero_wps_no_violation(self, service) -> None:
        violations = await _check(service, [])
        assert violations == []

    async def test_under_limit_no_violation(self, service) -> None:
        wps = [_make_wp(f"WP{i}") for i in range(3)]
        violations = await _check(service, wps)
        assert violations == []

    async def test_at_limit_no_violation(self, service) -> None:
        wps = [_make_wp(f"WP{i}") for i in range(5)]
        violations = await _check(service, wps)
        assert violations == []

    async def test_over_limit_produces_violation(self, service) -> None:
        wps = [_make_wp(f"WP{i}") for i in range(6)]
        violations = await _check(service, wps)
        codes = [v.rule_code for v in violations]
        assert "WP_PER_PROJECT" in codes
        wp_v = next(v for v in violations if v.rule_code == "WP_PER_PROJECT")
        assert wp_v.severity == "error"
        assert wp_v.current_value == 6
        assert wp_v.max_allowed == 5

    async def test_way_over_limit(self, service) -> None:
        wps = [_make_wp(f"WP{i}") for i in range(20)]
        violations = await _check(service, wps)
        wp_v = next(v for v in violations if v.rule_code == "WP_PER_PROJECT")
        assert wp_v.current_value == 20


# ── Tasks per work package ────────────────────────────────────────


class TestTasksPerWorkPackage:
    async def test_empty_wp_no_violation(self, service) -> None:
        violations = await _check(service, [_make_wp("WP1")])
        assert violations == []

    async def test_at_limit_no_violation(self, service) -> None:
        tasks = [_make_task(f"T{i}") for i in range(6)]
        violations = await _check(service, [_make_wp("WP1", tasks)])
        assert violations == []

    async def test_over_limit_produces_violation(self, service) -> None:
        tasks = [_make_task(f"T{i}") for i in range(7)]
        violations = await _check(service, [_make_wp("WP1", tasks)])
        codes = [v.rule_code for v in violations]
        assert "TASKS_PER_WP" in codes
        v = next(v for v in violations if v.rule_code == "TASKS_PER_WP")
        assert v.current_value == 7
        assert "WP1" in v.object_scope

    async def test_multiple_wps_only_violating_one(self, service) -> None:
        ok_wp = _make_wp("OK", [_make_task(f"T{i}") for i in range(3)])
        bad_wp = _make_wp("Bad", [_make_task(f"T{i}") for i in range(8)])
        violations = await _check(service, [ok_wp, bad_wp])
        wp_violations = [v for v in violations if v.rule_code == "TASKS_PER_WP"]
        assert len(wp_violations) == 1
        assert "Bad" in wp_violations[0].object_scope


# ── Total tasks per project ──────────────────────────────────────


class TestTotalTasks:
    async def test_under_limit_no_violation(self, service) -> None:
        wps = [_make_wp(f"WP{i}", [_make_task(f"T{j}") for j in range(5)]) for i in range(4)]
        violations = await _check(service, wps)
        codes = [v.rule_code for v in violations]
        assert "TASKS_PER_PROJECT" not in codes

    async def test_at_limit_no_violation(self, service) -> None:
        # 4 WPs x 5 tasks = 20 = limit
        wps = [_make_wp(f"WP{i}", [_make_task(f"T{j}") for j in range(5)]) for i in range(4)]
        violations = await _check(service, wps)
        codes = [v.rule_code for v in violations]
        assert "TASKS_PER_PROJECT" not in codes

    async def test_over_limit_produces_violation(self, service) -> None:
        # 4 WPs x 6 tasks = 24 > 20
        wps = [_make_wp(f"WP{i}", [_make_task(f"T{j}") for j in range(6)]) for i in range(4)]
        violations = await _check(service, wps)
        codes = [v.rule_code for v in violations]
        assert "TASKS_PER_PROJECT" in codes
        v = next(v for v in violations if v.rule_code == "TASKS_PER_PROJECT")
        assert v.current_value == 24


# ── EWU per task ─────────────────────────────────────────────────


class TestEwuPerTask:
    async def test_at_limit_no_violation(self, service) -> None:
        wps = [_make_wp("WP1", [_make_task("T1", ewu=8)])]
        violations = await _check(service, wps)
        codes = [v.rule_code for v in violations]
        assert "EWU_PER_TASK" not in codes

    async def test_over_limit_produces_violation(self, service) -> None:
        wps = [_make_wp("WP1", [_make_task("T1", ewu=9)])]
        violations = await _check(service, wps)
        codes = [v.rule_code for v in violations]
        assert "EWU_PER_TASK" in codes
        v = next(v for v in violations if v.rule_code == "EWU_PER_TASK")
        assert v.current_value == 9
        assert v.max_allowed == 8

    async def test_under_limit_no_violation(self, service) -> None:
        wps = [_make_wp("WP1", [_make_task("T1", ewu=3)])]
        violations = await _check(service, wps)
        codes = [v.rule_code for v in violations]
        assert "EWU_PER_TASK" not in codes

    async def test_zero_ewu_no_violation(self, service) -> None:
        wps = [_make_wp("WP1", [_make_task("T1", ewu=0)])]
        violations = await _check(service, wps)
        codes = [v.rule_code for v in violations]
        assert "EWU_PER_TASK" not in codes

    async def test_multiple_tasks_one_violating(self, service) -> None:
        wps = [_make_wp("WP1", [_make_task("OK", ewu=5), _make_task("Bad", ewu=10)])]
        violations = await _check(service, wps)
        ewu_violations = [v for v in violations if v.rule_code == "EWU_PER_TASK"]
        assert len(ewu_violations) == 1
        assert "Bad" in ewu_violations[0].object_scope


# ── Combined checks ──────────────────────────────────────────────


class TestCombinedChecks:
    async def test_valid_draft_no_violations(self, service) -> None:
        wps = [
            _make_wp("WP1", [_make_task("T1", ewu=3), _make_task("T2", ewu=5)]),
            _make_wp("WP2", [_make_task("T3", ewu=8)]),
        ]
        violations = await _check(service, wps)
        assert violations == []

    async def test_empty_draft_no_violations(self, service) -> None:
        violations = await _check(service, [])
        assert violations == []

    async def test_multiple_violations_combined(self, service) -> None:
        """A draft with too many WPs and a task with EWU over limit."""
        wps = [_make_wp(f"WP{i}", [_make_task("OverEWU", ewu=9)]) for i in range(6)]
        violations = await _check(service, wps)
        rule_codes = {v.rule_code for v in violations}
        assert "WP_PER_PROJECT" in rule_codes
        assert "EWU_PER_TASK" in rule_codes

    async def test_all_limits_violated_at_once(self, service) -> None:
        """Extreme case: violate WP count, tasks per WP, total tasks, and EWU."""
        tasks = [_make_task(f"T{i}", ewu=9) for i in range(7)]
        wps = [_make_wp(f"WP{i}", tasks) for i in range(6)]
        violations = await _check(service, wps)
        rule_codes = {v.rule_code for v in violations}
        assert "WP_PER_PROJECT" in rule_codes
        assert "TASKS_PER_WP" in rule_codes
        assert "TASKS_PER_PROJECT" in rule_codes
        assert "EWU_PER_TASK" in rule_codes
