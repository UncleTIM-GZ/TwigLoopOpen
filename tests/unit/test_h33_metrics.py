"""Tests for H3.3 — Metrics collector, cost estimation, health endpoint."""

from app.metrics import MetricsCollector, estimate_llm_cost, metrics


class TestMetricsCollector:
    def test_increment_counter(self):
        m = MetricsCollector()
        m.inc("test_counter")
        m.inc("test_counter")
        snap = m.snapshot()
        assert snap["counters"]["test_counter"] == 2

    def test_labeled_counter(self):
        m = MetricsCollector()
        m.inc("calls", provider="gemini", model="flash")
        m.inc("calls", provider="anthropic", model="sonnet")
        snap = m.snapshot()
        assert snap["counters"]["calls{model=flash,provider=gemini}"] == 1
        assert snap["counters"]["calls{model=sonnet,provider=anthropic}"] == 1

    def test_timing(self):
        m = MetricsCollector()
        for v in [100, 200, 300, 400, 500]:
            m.timing("latency", float(v))
        snap = m.snapshot()
        t = snap["timings"]["latency"]
        assert t["count"] == 5
        assert t["p50"] == 300.0
        assert t["avg"] == 300.0

    def test_gauge(self):
        m = MetricsCollector()
        m.gauge("active_connections", 42.0)
        snap = m.snapshot()
        assert snap["gauges"]["active_connections"] == 42.0

    def test_snapshot_is_dict(self):
        snap = metrics.snapshot()
        assert "counters" in snap
        assert "gauges" in snap
        assert "timings" in snap


class TestLLMCostEstimation:
    def test_gemini_free_tier(self):
        cost = estimate_llm_cost("gemini-3.1-flash-lite-preview", 100, 50)
        assert cost == 0.0

    def test_anthropic_cost(self):
        cost = estimate_llm_cost("claude-sonnet-4-20250514", 1000, 500)
        assert cost > 0
        # 1000 input tokens * $3/1M + 500 output tokens * $15/1M
        expected = (1000 / 1_000_000) * 3.0 + (500 / 1_000_000) * 15.0
        assert abs(cost - expected) < 0.0001

    def test_unknown_model_uses_default(self):
        cost = estimate_llm_cost("unknown-model", 1000, 500)
        assert cost > 0


class TestMetricsIntegration:
    def test_llm_client_records_metrics(self):
        """Verify llm_client has metrics recording code."""
        import inspect

        from app.services.agents.llm_client import generate_structured

        source = inspect.getsource(generate_structured)
        assert "metrics.inc" in source
        assert "metrics.timing" in source
        assert "llm_calls_total" in source

    def test_coordination_service_records_metrics(self):
        """Verify CoordinationService has metrics recording code."""
        import inspect

        from app.services.coordination_service import CoordinationService

        source = inspect.getsource(CoordinationService._execute_delegation)
        assert "metrics.inc" in source
        assert "delegation_total" in source

    def test_health_endpoint_exists(self):
        """Verify /metrics endpoint exists in app."""
        from app.main import app

        routes = [r.path for r in app.routes]
        assert "/metrics" in routes
        assert "/health" in routes
