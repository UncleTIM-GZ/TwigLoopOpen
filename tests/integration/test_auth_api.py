"""Integration tests for /api/v1/auth endpoints."""

import pytest

from tests.helpers.assertions import assert_api_error, assert_api_success, assert_status_code

# Cookie names must match the constants in auth.py
_ACCESS_COOKIE = "twigloop_access_token"
_REFRESH_COOKIE = "twigloop_refresh_token"


class TestRegister:
    async def test_register_success(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "new@example.com",
            "password": "securepassword123",
            "display_name": "New User",
            "entry_intent": "both",
        })
        assert_status_code(resp, 201)
        data = assert_api_success(resp.json())
        assert "account_id" in data
        assert "actor_id" in data
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_register_duplicate_email(self, client):
        payload = {
            "email": "dup@example.com",
            "password": "securepassword123",
            "display_name": "First User",
            "entry_intent": "founder",
        }
        resp1 = await client.post("/api/v1/auth/register", json=payload)
        assert_status_code(resp1, 201)

        resp2 = await client.post("/api/v1/auth/register", json=payload)
        assert_status_code(resp2, 409)
        assert_api_error(resp2.json(), expected_fragment="already registered")

    async def test_register_invalid_email(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "securepassword123",
            "display_name": "Bad",
            "entry_intent": "founder",
        })
        assert_status_code(resp, 422)

    async def test_register_short_password(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "short@example.com",
            "password": "short",
            "display_name": "Short PW",
            "entry_intent": "founder",
        })
        assert_status_code(resp, 422)

    async def test_register_founder_intent(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "founder-intent@example.com",
            "password": "securepassword123",
            "display_name": "Founder",
            "entry_intent": "founder",
        })
        assert_status_code(resp, 201)
        data = assert_api_success(resp.json())
        assert data["account_id"] is not None

    async def test_register_collaborator_intent(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "collab-intent@example.com",
            "password": "securepassword123",
            "display_name": "Collaborator",
            "entry_intent": "collaborator",
        })
        assert_status_code(resp, 201)


class TestLogin:
    async def test_login_success(self, client):
        # First register
        await client.post("/api/v1/auth/register", json={
            "email": "login@example.com",
            "password": "securepassword123",
            "display_name": "Login User",
            "entry_intent": "both",
        })

        resp = await client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "securepassword123",
        })
        assert_status_code(resp, 200)
        data = assert_api_success(resp.json())
        assert "access_token" in data

    async def test_login_wrong_password(self, client):
        await client.post("/api/v1/auth/register", json={
            "email": "wrongpw@example.com",
            "password": "securepassword123",
            "display_name": "Wrong PW",
            "entry_intent": "both",
        })

        resp = await client.post("/api/v1/auth/login", json={
            "email": "wrongpw@example.com",
            "password": "wrongpassword000",
        })
        assert_status_code(resp, 401)

    async def test_login_nonexistent_email(self, client):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "doesnotmatter",
        })
        assert_status_code(resp, 401)


class TestAuthCookies:
    """Verify httpOnly cookie behaviour on auth endpoints (P1-4)."""

    async def _register(self, client):
        """Helper: register a user and return the response."""
        return await client.post("/api/v1/auth/register", json={
            "email": "cookie-test@example.com",
            "password": "securepassword123",
            "display_name": "Cookie User",
            "entry_intent": "both",
        })

    async def test_register_sets_cookies(self, client):
        resp = await self._register(client)
        assert_status_code(resp, 201)
        cookies = {c.name: c for c in resp.cookies.jar}
        assert _ACCESS_COOKIE in cookies, f"Expected {_ACCESS_COOKIE} cookie"
        assert _REFRESH_COOKIE in cookies, f"Expected {_REFRESH_COOKIE} cookie"

    async def test_login_sets_cookies(self, client):
        await self._register(client)
        resp = await client.post("/api/v1/auth/login", json={
            "email": "cookie-test@example.com",
            "password": "securepassword123",
        })
        assert_status_code(resp, 200)
        cookies = {c.name: c for c in resp.cookies.jar}
        assert _ACCESS_COOKIE in cookies
        assert _REFRESH_COOKIE in cookies

    async def test_cookie_auth_fallback(self, client):
        """Authenticated endpoint works when token is sent via cookie only."""
        reg_resp = await self._register(client)
        data = assert_api_success(reg_resp.json())
        token = data["access_token"]

        # Request with cookie only (no Authorization header)
        resp = await client.get(
            "/api/v1/me",
            cookies={_ACCESS_COOKIE: token},
        )
        assert_status_code(resp, 200)
        me = assert_api_success(resp.json())
        assert me["account"]["email"] == "cookie-test@example.com"

    async def test_logout_returns_success(self, client):
        resp = await client.post("/api/v1/auth/logout")
        assert_status_code(resp, 200)
        body = resp.json()
        assert body["success"] is True
