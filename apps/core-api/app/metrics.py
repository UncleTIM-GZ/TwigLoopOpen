"""Platform metrics — in-process counters for key operational paths.

Lightweight metrics collection without external dependencies.
Counters are thread-safe via simple dict + atomic increments.
Export via /metrics endpoint or structured logging.
"""

from collections import defaultdict
from threading import Lock
from typing import Any


class MetricsCollector:
    """Simple in-process metrics collector."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: dict[str, int] = defaultdict(int)
        self._timings: dict[str, list[float]] = defaultdict(list)
        self._gauges: dict[str, float] = {}

    def inc(self, name: str, value: int = 1, **labels: str) -> None:
        key = self._key(name, labels)
        with self._lock:
            self._counters[key] += value

    def timing(self, name: str, ms: float, **labels: str) -> None:
        key = self._key(name, labels)
        with self._lock:
            timings = self._timings[key]
            timings.append(ms)
            if len(timings) > 1000:
                self._timings[key] = timings[-500:]

    def gauge(self, name: str, value: float, **labels: str) -> None:
        key = self._key(name, labels)
        with self._lock:
            self._gauges[key] = value

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            result: dict[str, Any] = {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "timings": {},
            }
            for key, values in self._timings.items():
                if values:
                    sorted_v = sorted(values)
                    n = len(sorted_v)
                    result["timings"][key] = {
                        "count": n,
                        "p50": sorted_v[n // 2],
                        "p95": sorted_v[int(n * 0.95)] if n >= 20 else sorted_v[-1],
                        "avg": sum(sorted_v) / n,
                    }
            return result

    @staticmethod
    def _key(name: str, labels: dict[str, str]) -> str:
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"


# Global singleton
metrics = MetricsCollector()


# Pricing table (USD per 1M tokens, estimated)
LLM_PRICING: dict[str, dict[str, float]] = {
    "gemini-3.1-flash-lite-preview": {"input": 0.0, "output": 0.0},
    "gemini-2.0-flash-lite": {"input": 0.0, "output": 0.0},
    "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
}


def estimate_llm_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate cost in USD based on token counts."""
    pricing = LLM_PRICING.get(model, {"input": 1.0, "output": 3.0})
    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]
    return round(input_cost + output_cost, 6)
