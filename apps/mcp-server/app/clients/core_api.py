"""HTTP client for calling core-api from MCP Server."""

import os
from typing import Any

import httpx

CORE_API_BASE = os.getenv("CORE_API_BASE_URL", "http://localhost:8000")

_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    """Get or create the shared httpx client."""
    global _client  # noqa: PLW0603
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(base_url=CORE_API_BASE, timeout=30.0)
    return _client


async def close_client() -> None:
    """Close the httpx client."""
    global _client  # noqa: PLW0603
    if _client and not _client.is_closed:
        await _client.aclose()
    _client = None


async def call_core_api(
    method: str,
    path: str,
    token: str | None = None,
    json_body: dict[str, Any] | None = None,
    params: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Call core-api and return JSON response. Raises on HTTP errors."""
    client = await get_client()
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = await client.request(
        method=method,
        url=path,
        json=json_body,
        params=params,
        headers=headers,
    )
    data: dict[str, Any] = response.json()

    if response.status_code >= 400:
        error_msg = data.get("error") or data.get("detail") or "Upstream error"
        raise RuntimeError(f"core-api error ({response.status_code}): {error_msg}")

    return data
