"""Integration tests for /api/v1/webhooks/github endpoint."""

import json

import pytest

from tests.helpers.assertions import assert_api_success, assert_status_code


class TestGitHubWebhook:
    """Test the GitHub webhook receiver.

    These tests verify payload parsing and response format.
    Since tests use an in-memory DB without source bindings,
    most events will be 'ignored' — which is the expected behavior.
    """

    async def test_unsupported_event_ignored(self, client):
        resp = await client.post(
            "/api/v1/webhooks/github",
            content=json.dumps({"action": "created"}).encode(),
            headers={
                "X-GitHub-Event": "star",
                "Content-Type": "application/json",
            },
        )
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["status"] == "ignored"

    async def test_push_event_without_binding(self, client):
        payload = {
            "ref": "refs/heads/main",
            "after": "abc123",
            "commits": [{"id": "abc123", "message": "test commit"}],
            "pusher": {"name": "testuser"},
            "repository": {"html_url": "https://github.com/test/unbound-repo"},
        }
        resp = await client.post(
            "/api/v1/webhooks/github",
            content=json.dumps(payload).encode(),
            headers={
                "X-GitHub-Event": "push",
                "Content-Type": "application/json",
            },
        )
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        # No binding exists, so the event should be ignored
        assert data["status"] == "ignored"

    async def test_pr_event_without_binding(self, client):
        payload = {
            "action": "opened",
            "pull_request": {
                "number": 42,
                "title": "Test PR",
                "user": {"login": "testuser"},
            },
            "repository": {"html_url": "https://github.com/test/unbound-repo"},
        }
        resp = await client.post(
            "/api/v1/webhooks/github",
            content=json.dumps(payload).encode(),
            headers={
                "X-GitHub-Event": "pull_request",
                "Content-Type": "application/json",
            },
        )
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["status"] == "ignored"

    async def test_invalid_json_returns_error(self, client):
        resp = await client.post(
            "/api/v1/webhooks/github",
            content=b"not json at all",
            headers={
                "X-GitHub-Event": "push",
                "Content-Type": "application/json",
            },
        )
        assert_status_code(resp, 200)
        body = resp.json()
        assert body["success"] is False

    async def test_missing_repo_url_ignored(self, client):
        payload = {
            "ref": "refs/heads/main",
            "after": "abc123",
            "commits": [],
            "pusher": {"name": "testuser"},
            # No "repository" key
        }
        resp = await client.post(
            "/api/v1/webhooks/github",
            content=json.dumps(payload).encode(),
            headers={
                "X-GitHub-Event": "push",
                "Content-Type": "application/json",
            },
        )
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert data["status"] == "ignored"
