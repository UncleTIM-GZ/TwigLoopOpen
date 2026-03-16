"""HTTP client for calling core-api from Temporal activities."""

import os
from typing import Any

import httpx

CORE_API_BASE = os.getenv("CORE_API_BASE_URL", "http://localhost:8000")


async def call_core_api(
    method: str,
    path: str,
    token: str | None = None,
    json_body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call core-api and return JSON response.

    Each activity call creates a fresh httpx client because Temporal activities
    may run in different threads/processes. This is intentional — activity
    executions should be stateless.
    """
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(base_url=CORE_API_BASE, timeout=30.0) as client:
        response = await client.request(
            method=method,
            url=path,
            json=json_body,
            headers=headers,
        )
        data: dict[str, Any] = response.json()

        if response.status_code >= 400:
            error_msg = data.get("error") or data.get("detail") or "Upstream error"
            raise RuntimeError(f"core-api error ({response.status_code}): {error_msg}")

        return data
