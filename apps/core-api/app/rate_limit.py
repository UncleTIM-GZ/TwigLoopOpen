"""Simple in-memory rate limiter for public endpoints.

Uses a sliding window counter per client IP. Not distributed — suitable for
single-instance deployments and MVP. Replace with Redis-backed limiter for
multi-instance production.
"""

import time
from collections import defaultdict

from fastapi import HTTPException, Request


class RateLimiter:
    """Sliding window rate limiter keyed by client IP."""

    def __init__(self, max_requests: int = 30, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def reset(self) -> None:
        """Clear all tracked hits. Useful for testing."""
        self._hits.clear()

    def __call__(self, request: Request) -> None:
        key = self._client_key(request)
        now = time.monotonic()
        cutoff = now - self.window_seconds

        # Prune old entries
        hits = self._hits[key]
        self._hits[key] = [t for t in hits if t > cutoff]

        if len(self._hits[key]) >= self.max_requests:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later.",
            )
        self._hits[key].append(now)


# Shared instances — use as FastAPI Depends
public_rate_limit = RateLimiter(max_requests=30, window_seconds=60)
auth_rate_limit = RateLimiter(max_requests=10, window_seconds=60)
