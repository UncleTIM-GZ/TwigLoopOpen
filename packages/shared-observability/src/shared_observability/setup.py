"""Telemetry initialization for all services."""

import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


def setup_telemetry(service_name: str) -> None:
    """Initialize OpenTelemetry and structured logging for a service."""
    # Tracer
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    # Structured logging
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    )

    logger = structlog.get_logger()
    logger.info("telemetry_initialized", service=service_name)
