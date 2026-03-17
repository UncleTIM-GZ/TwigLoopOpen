"""Tests for Horizon 2.4 — Observability, trace context, structured logging."""

import uuid

from app.observability import (
    get_trace_context,
    get_trace_id,
    log_event,
    set_trace_context,
)


class TestTraceContext:
    """Test contextvars-based trace propagation."""

    def test_set_and_get_trace_id(self):
        tid = str(uuid.uuid4())
        set_trace_context(trace_id=tid)
        assert get_trace_id() == tid

    def test_get_trace_context_dict(self):
        tid = str(uuid.uuid4())
        cid = str(uuid.uuid4())
        set_trace_context(trace_id=tid, correlation_id=cid, task_id="t1", actor_id="a1")
        ctx = get_trace_context()
        assert ctx["trace_id"] == tid
        assert ctx["correlation_id"] == cid
        assert ctx["task_id"] == "t1"
        assert ctx["actor_id"] == "a1"

    def test_context_preserves_previous_values(self):
        """Setting empty string doesn't clear — only non-empty values are set."""
        tid = str(uuid.uuid4())
        set_trace_context(trace_id=tid)
        # Empty string won't overwrite
        set_trace_context(trace_id="")
        assert get_trace_id() == tid


class TestLogEvent:
    """Test structured log event emission."""

    def test_log_event_does_not_raise(self):
        log_event(
            "test_event",
            service_name="core-api",
            agent_name="matching_agent",
            result_status="success",
            latency_ms=42,
            delegation_id="del-1",
            trace_id="trace-1",
        )

    def test_log_event_with_llm_fields(self):
        log_event(
            "llm_call_completed",
            provider="gemini",
            model="gemini-3.1-flash-lite-preview",
            latency_ms=1200,
            result_status="success",
        )

    def test_log_event_with_fallback(self):
        log_event(
            "delegation_fallback",
            agent_name="vc_agent",
            fallback_reason="external_agent_failed",
            error_code="connection_timeout",
        )


class TestCoordinationServiceObservability:
    """Verify CoordinationService logs include observability fields."""

    def test_delegation_log_fields_documented(self):
        """Ensure key log fields are present in delegation code."""
        import inspect

        from app.services.coordination_service import CoordinationService

        source = inspect.getsource(CoordinationService._execute_delegation)
        assert "event_type" in source
        assert "delegation_id" in source
        assert "trace_id" in source
        assert "latency_ms" in source
        assert "fallback_used" in source
        assert "result_status" in source


class TestLLMClientObservability:
    """Verify LLM client logs include observability fields."""

    def test_llm_log_fields_documented(self):
        import inspect

        from app.services.agents.llm_client import generate_structured

        source = inspect.getsource(generate_structured)
        assert "agent_name" in source
        assert "trace_id" in source
        assert "task_id" in source
        assert "provider" in source
        assert "latency_ms" in source
        assert "failure_type" in source

    def test_generate_structured_accepts_trace_params(self):
        """Verify the function signature accepts trace context."""
        import inspect

        from app.services.agents.llm_client import generate_structured

        sig = inspect.signature(generate_structured)
        params = list(sig.parameters.keys())
        assert "agent_name" in params
        assert "trace_id" in params
        assert "task_id" in params
