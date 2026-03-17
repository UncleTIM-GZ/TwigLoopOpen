"""Platform observability — unified trace context and structured logging helpers.

Provides request-scoped trace context propagation via contextvars,
and structured logging helpers for consistent observability across
all platform services, agents, and external calls.
"""

import logging
import time
import uuid
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Context variables for request-scoped trace propagation
_trace_id: ContextVar[str] = ContextVar("trace_id", default="")
_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")
_task_id: ContextVar[str] = ContextVar("task_id", default="")
_actor_id: ContextVar[str] = ContextVar("actor_id", default="")


def get_trace_id() -> str:
    return _trace_id.get()


def get_correlation_id() -> str:
    return _correlation_id.get()


def set_trace_context(
    *,
    trace_id: str = "",
    correlation_id: str = "",
    task_id: str = "",
    actor_id: str = "",
) -> None:
    """Set trace context for the current request scope."""
    if trace_id:
        _trace_id.set(trace_id)
    if correlation_id:
        _correlation_id.set(correlation_id)
    if task_id:
        _task_id.set(task_id)
    if actor_id:
        _actor_id.set(actor_id)


def get_trace_context() -> dict[str, str]:
    """Get current trace context as a dict (for log enrichment)."""
    ctx: dict[str, str] = {}
    if _trace_id.get():
        ctx["trace_id"] = _trace_id.get()
    if _correlation_id.get():
        ctx["correlation_id"] = _correlation_id.get()
    if _task_id.get():
        ctx["task_id"] = _task_id.get()
    if _actor_id.get():
        ctx["actor_id"] = _actor_id.get()
    return ctx


def log_event(
    event_type: str,
    *,
    service_name: str = "core-api",
    agent_name: str = "",
    result_status: str = "",
    latency_ms: int = 0,
    delegation_id: str = "",
    provider: str = "",
    model: str = "",
    fallback_reason: str = "",
    error_code: str = "",
    **extra: Any,
) -> None:
    """Emit a structured observability event with trace context."""
    fields: dict[str, Any] = {
        "event_type": event_type,
        "service_name": service_name,
        **get_trace_context(),
    }
    if agent_name:
        fields["agent_name"] = agent_name
    if result_status:
        fields["result_status"] = result_status
    if latency_ms:
        fields["latency_ms"] = latency_ms
    if delegation_id:
        fields["delegation_id"] = delegation_id
    if provider:
        fields["provider"] = provider
    if model:
        fields["model"] = model
    if fallback_reason:
        fields["fallback_reason"] = fallback_reason
    if error_code:
        fields["error_code"] = error_code
    fields.update(extra)

    logger.info(event_type, extra=fields)


class TraceContextMiddleware(BaseHTTPMiddleware):
    """Injects trace_id into every request via contextvars."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        # Use incoming trace header or generate new
        trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
        correlation_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))

        set_trace_context(trace_id=trace_id, correlation_id=correlation_id)

        start = time.monotonic()
        response: Response = await call_next(request)
        latency_ms = int((time.monotonic() - start) * 1000)

        # Add trace headers to response
        response.headers["X-Trace-Id"] = trace_id

        # Log request completion
        log_event(
            "http_request_completed",
            result_status=str(response.status_code),
            latency_ms=latency_ms,
            method=request.method,
            path=request.url.path,
        )

        return response
