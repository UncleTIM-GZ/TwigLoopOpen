"""Integration tests for /api/v1/quotas endpoints."""

import uuid

from app.domain.quota_config import (
    MAX_EWU_PER_TASK,
    MAX_TASKS_PER_PROJECT,
    MAX_TASKS_PER_WORK_PACKAGE,
    MAX_WORK_PACKAGES_PER_PROJECT,
)

from tests.helpers.assertions import assert_api_success, assert_status_code
from tests.helpers.auth import auth_header


class TestGetQuotaRules:
    async def test_get_rules_returns_all_sections(self, client) -> None:
        resp = await client.get("/api/v1/quotas/rules")
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert "object_limits" in data
        assert "founder_limits" in data
        assert "relationship_limits" in data
        assert "status_definitions" in data

    async def test_object_limits_values(self, client) -> None:
        resp = await client.get("/api/v1/quotas/rules")
        limits = assert_api_success(resp.json())["object_limits"]
        assert limits["max_work_packages_per_project"] == MAX_WORK_PACKAGES_PER_PROJECT
        assert limits["max_tasks_per_work_package"] == MAX_TASKS_PER_WORK_PACKAGE
        assert limits["max_tasks_per_project"] == MAX_TASKS_PER_PROJECT
        assert limits["max_ewu_per_task"] == MAX_EWU_PER_TASK

    async def test_status_definitions_are_lists(self, client) -> None:
        resp = await client.get("/api/v1/quotas/rules")
        statuses = assert_api_success(resp.json())["status_definitions"]
        for key in ("active_project_statuses", "open_seat_statuses",
                     "active_task_statuses", "pending_application_statuses"):
            assert isinstance(statuses[key], list)
            assert len(statuses[key]) > 0


class TestCheckProjectQuota:
    async def test_valid_project_passes(
        self, client, founder_account, founder_actor,
    ) -> None:
        headers = auth_header(founder_account.id, founder_actor.id)
        resp = await client.post("/api/v1/quotas/check-project", json={
            "work_packages": [
                {
                    "title": f"WP{i}",
                    "tasks": [{"title": f"T{j}", "ewu": 4} for j in range(3)],
                }
                for i in range(3)
            ],
        }, headers=headers)
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["passed"] is True
        assert data["violations"] == []

    async def test_over_wp_limit_returns_violation(
        self, client, founder_account, founder_actor,
    ) -> None:
        headers = auth_header(founder_account.id, founder_actor.id)
        resp = await client.post("/api/v1/quotas/check-project", json={
            "work_packages": [
                {"title": f"WP{i}", "tasks": []}
                for i in range(MAX_WORK_PACKAGES_PER_PROJECT + 1)
            ],
        }, headers=headers)
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["passed"] is False
        codes = [v["rule_code"] for v in data["violations"]]
        assert "WP_PER_PROJECT" in codes

    async def test_over_ewu_returns_violation(
        self, client, founder_account, founder_actor,
    ) -> None:
        headers = auth_header(founder_account.id, founder_actor.id)
        resp = await client.post("/api/v1/quotas/check-project", json={
            "work_packages": [
                {
                    "title": "WP1",
                    "tasks": [{"title": "OverEWU", "ewu": MAX_EWU_PER_TASK + 1}],
                },
            ],
        }, headers=headers)
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["passed"] is False
        codes = [v["rule_code"] for v in data["violations"]]
        assert "EWU_PER_TASK" in codes

    async def test_empty_project_passes(
        self, client, founder_account, founder_actor,
    ) -> None:
        headers = auth_header(founder_account.id, founder_actor.id)
        resp = await client.post("/api/v1/quotas/check-project", json={
            "work_packages": [],
        }, headers=headers)
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["passed"] is True

    async def test_unauthenticated_returns_401(self, client) -> None:
        resp = await client.post("/api/v1/quotas/check-project", json={
            "work_packages": [],
        })
        assert resp.status_code in (401, 403)


class TestCheckApplicationQuota:
    async def test_application_check_passes_with_no_pending(
        self, client, founder_account, founder_actor,
    ) -> None:
        headers = auth_header(founder_account.id, founder_actor.id)
        project_id = str(uuid.uuid4())
        resp = await client.post("/api/v1/quotas/check-application", json={
            "project_id": project_id,
        }, headers=headers)
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["passed"] is True
        assert data["violations"] == []

    async def test_application_check_with_task_id(
        self, client, founder_account, founder_actor,
    ) -> None:
        headers = auth_header(founder_account.id, founder_actor.id)
        resp = await client.post("/api/v1/quotas/check-application", json={
            "project_id": str(uuid.uuid4()),
            "task_id": str(uuid.uuid4()),
        }, headers=headers)
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["passed"] is True

    async def test_unauthenticated_returns_401(self, client) -> None:
        resp = await client.post("/api/v1/quotas/check-application", json={
            "project_id": str(uuid.uuid4()),
        })
        assert resp.status_code in (401, 403)
