"""Integration tests for /api/v1/projects endpoints."""

import pytest

from tests.helpers.assertions import assert_api_error, assert_api_success, assert_status_code
from tests.helpers.auth import auth_header


class TestCreateProject:
    async def test_create_general_project(self, client, founder_account, founder_actor):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "My General Project",
            "summary": "A test general project",
        }, headers=headers)
        assert_status_code(resp, 201)
        data = assert_api_success(resp.json())
        assert data["project_type"] == "general"
        assert data["status"] == "draft"
        assert data["needs_human_reviewer"] is False
        assert data["has_reward"] is False

    async def test_create_public_benefit_project(self, client, founder_account, founder_actor):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        resp = await client.post("/api/v1/projects/", json={
            "project_type": "public_benefit",
            "founder_type": "ordinary",
            "title": "PB Project",
            "summary": "Public benefit project",
        }, headers=headers)
        assert_status_code(resp, 201)
        data = assert_api_success(resp.json())
        assert data["needs_human_reviewer"] is True
        assert data["human_review_status"] == "reviewer_required"

    async def test_create_recruitment_project(self, client, founder_account, founder_actor):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        resp = await client.post("/api/v1/projects/", json={
            "project_type": "recruitment",
            "founder_type": "ordinary",
            "title": "Recruitment Project",
            "summary": "Hiring",
        }, headers=headers)
        assert_status_code(resp, 201)
        data = assert_api_success(resp.json())
        assert data["has_reward"] is True

    async def test_create_project_non_founder_forbidden(
        self, client, collaborator_account, collaborator_actor
    ):
        headers = auth_header(
            collaborator_account.id, collaborator_actor.id, ("collaborator",)
        )
        resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Should Fail",
            "summary": "Non-founder attempt",
        }, headers=headers)
        assert_status_code(resp, 403)

    async def test_create_project_without_auth(self, client):
        resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "No Auth",
            "summary": "Should fail",
        })
        assert_status_code(resp, 401)


class TestListProjects:
    async def test_list_empty(self, client):
        resp = await client.get("/api/v1/projects/")
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert isinstance(data, list)

    async def test_list_with_project(self, client, founder_account, founder_actor):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Listed Project",
            "summary": "Should appear",
        }, headers=headers)

        resp = await client.get("/api/v1/projects/")
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert len(data) >= 1

    async def test_list_filter_by_type(self, client, founder_account, founder_actor):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        await client.post("/api/v1/projects/", json={
            "project_type": "recruitment",
            "founder_type": "ordinary",
            "title": "Filtered",
            "summary": "For filter test",
        }, headers=headers)

        resp = await client.get("/api/v1/projects/?project_type=recruitment")
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        for p in data:
            assert p["project_type"] == "recruitment"


class TestGetProject:
    async def test_get_existing_project(self, client, founder_account, founder_actor):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Get Test",
            "summary": "Test get",
        }, headers=headers)
        project_id = create_resp.json()["data"]["project_id"]

        resp = await client.get(f"/api/v1/projects/{project_id}")
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["title"] == "Get Test"

    async def test_get_nonexistent_project(self, client):
        resp = await client.get("/api/v1/projects/00000000-0000-0000-0000-000000000099")
        assert_status_code(resp, 404)


class TestUpdateProject:
    async def test_update_title(self, client, founder_account, founder_actor):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Original",
            "summary": "Original summary",
        }, headers=headers)
        project_id = create_resp.json()["data"]["project_id"]

        resp = await client.patch(
            f"/api/v1/projects/{project_id}",
            json={"title": "Updated Title"},
            headers=headers,
        )
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["title"] == "Updated Title"

    async def test_update_by_non_owner_forbidden(
        self, client, founder_account, founder_actor,
        new_founder_account, new_founder_actor,
    ):
        owner_headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Owner Only",
            "summary": "Only owner can update",
        }, headers=owner_headers)
        project_id = create_resp.json()["data"]["project_id"]

        other_headers = auth_header(
            new_founder_account.id, new_founder_actor.id, ("founder",)
        )
        resp = await client.patch(
            f"/api/v1/projects/{project_id}",
            json={"title": "Hijacked"},
            headers=other_headers,
        )
        assert_status_code(resp, 403)


class TestProjectStatusTransition:
    async def test_draft_to_open(self, client, founder_account, founder_actor):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Status Test",
            "summary": "For status transition",
        }, headers=headers)
        project_id = create_resp.json()["data"]["project_id"]

        resp = await client.patch(
            f"/api/v1/projects/{project_id}/status",
            json={"status": "open_for_collaboration"},
            headers=headers,
        )
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["status"] == "open_for_collaboration"

    async def test_invalid_transition(self, client, founder_account, founder_actor):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        create_resp = await client.post("/api/v1/projects/", json={
            "project_type": "general",
            "founder_type": "ordinary",
            "title": "Invalid Transition",
            "summary": "Should fail",
        }, headers=headers)
        project_id = create_resp.json()["data"]["project_id"]

        resp = await client.patch(
            f"/api/v1/projects/{project_id}/status",
            json={"status": "in_progress"},
            headers=headers,
        )
        assert_status_code(resp, 409)
