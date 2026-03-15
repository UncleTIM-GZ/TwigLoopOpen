"""Integration tests for profile endpoints (GET/PATCH /me)."""

from tests.helpers.assertions import assert_api_success, assert_status_code
from tests.helpers.auth import auth_header


class TestGetProfile:
    async def test_get_me_success(
        self, client, founder_account, founder_actor,
    ):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        resp = await client.get("/api/v1/me", headers=headers)
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert "account" in data
        assert "actor" in data
        assert data["actor"]["display_name"] == founder_actor.display_name


class TestUpdateProfile:
    async def test_update_bio(
        self, client, founder_account, founder_actor,
    ):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        resp = await client.patch("/api/v1/me", json={
            "bio": "Updated bio text",
        }, headers=headers)
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["bio"] == "Updated bio text"

    async def test_update_skills(
        self, client, founder_account, founder_actor,
    ):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        resp = await client.patch("/api/v1/me", json={
            "skills": ["python", "react", "figma"],
        }, headers=headers)
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["skills"] == ["python", "react", "figma"]

    async def test_update_interested_project_types(
        self, client, founder_account, founder_actor,
    ):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        resp = await client.patch("/api/v1/me", json={
            "interested_project_types": ["general", "public_benefit"],
        }, headers=headers)
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["interested_project_types"] == ["general", "public_benefit"]

    async def test_update_multiple_fields(
        self, client, founder_account, founder_actor,
    ):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        resp = await client.patch("/api/v1/me", json={
            "display_name": "New Name",
            "bio": "New bio",
            "availability": "20h/week",
            "skills": ["go", "rust"],
            "interested_project_types": ["recruitment"],
        }, headers=headers)
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["display_name"] == "New Name"
        assert data["bio"] == "New bio"
        assert data["availability"] == "20h/week"
        assert data["skills"] == ["go", "rust"]
        assert data["interested_project_types"] == ["recruitment"]
