"""Integration tests for VC credential endpoints."""

import uuid

from tests.helpers.assertions import assert_api_success, assert_status_code
from tests.helpers.auth import auth_header


class TestVerifyCredential:
    async def test_verify_nonexistent_returns_invalid(self, client):
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"/api/v1/credentials/verify/{fake_id}")
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["valid"] is False
        assert data["credential_type"] is None
        assert data["issued_at"] is None
        # Verify no internal IDs leaked
        assert "actor_id" not in data
        assert "credential_data" not in data


class TestListMyCredentials:
    async def test_empty_list(
        self, client, founder_account, founder_actor,
    ):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        resp = await client.get("/api/v1/me/credentials", headers=headers)
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data == []


class TestGetCredential:
    async def test_not_found(
        self, client, founder_account, founder_actor,
    ):
        headers = auth_header(founder_account.id, founder_actor.id, ("founder",))
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"/api/v1/credentials/{fake_id}", headers=headers)
        assert_status_code(resp, 404)
