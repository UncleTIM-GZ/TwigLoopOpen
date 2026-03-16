"""NATS JetStream event publisher."""

import asyncio
import json
import logging
import uuid
from datetime import UTC, datetime

import nats
from nats.aio.client import Client as NATSClient
from nats.js import JetStreamContext
from pydantic import BaseModel
from shared_config import NATSSettings

_settings = NATSSettings()
_logger = logging.getLogger(__name__)

# Module-level connection (initialized via lifespan)
_nc: NATSClient | None = None
_js: JetStreamContext | None = None


async def connect_nats() -> None:
    """Connect to NATS and enable JetStream with auto-created streams."""
    global _nc, _js  # noqa: PLW0603
    try:
        _nc = await nats.connect(_settings.nats_url, connect_timeout=5)
        _js = _nc.jetstream()
    except Exception:
        _logger.warning("Failed to connect to NATS, events will be skipped")
        _nc = None
        _js = None
        return

    # Create streams — safe if already exist
    import contextlib

    from nats.js.api import StreamConfig
    from nats.js.errors import BadRequestError

    for stream_name, subjects in [
        ("ACCOUNT", ["account.>"]),
        ("PROJECT", ["project.>"]),
        ("REVIEW", ["review.>"]),
        ("SOURCE", ["source.>"]),
        ("CREDENTIAL", ["credential.>"]),
        ("SPONSOR", ["sponsor.>"]),
    ]:
        with contextlib.suppress(BadRequestError):
            await _js.add_stream(StreamConfig(name=stream_name, subjects=subjects))


async def disconnect_nats() -> None:
    """Gracefully close NATS connection."""
    global _nc, _js  # noqa: PLW0603
    if _nc and not _nc.is_closed:
        await _nc.close()
    _nc = None
    _js = None


class DomainEvent(BaseModel):
    """Standard domain event envelope."""

    event_id: str
    event_type: str
    occurred_at: str
    actor_id: str | None = None
    payload: dict[str, object]


async def publish_event(
    subject: str,
    payload: dict[str, object],
    actor_id: uuid.UUID | None = None,
) -> None:
    """Publish a domain event to NATS JetStream. Never raises.

    KNOWN LIMITATIONS (tech debt — see docs/audit-report.md):
    - Best-effort delivery: events may be silently dropped if NATS is unavailable.
    - Called BEFORE database commit: if the DB transaction rolls back after this
      call, the event is already published — downstream consumers may see an event
      for a record that does not exist. Proper fix requires outbox pattern.
    - Retry budget: 3 retries with 0.1/0.5/1.0s delays. Total worst-case blocking
      time is ~1.6s per call on persistent failure.
    """
    if _js is None:
        _logger.warning("NATS not connected, dropping event %s (actor=%s)", subject, actor_id)
        return

    event = DomainEvent(
        event_id=str(uuid.uuid4()),
        event_type=subject,
        occurred_at=datetime.now(UTC).isoformat(),
        actor_id=str(actor_id) if actor_id else None,
        payload=payload,
    )
    data = json.dumps(event.model_dump()).encode()
    _retry_delays = [0.1, 0.5, 1.0]
    for attempt in range(len(_retry_delays) + 1):
        try:
            await _js.publish(subject, data)
            return
        except Exception:
            if attempt < len(_retry_delays):
                await asyncio.sleep(_retry_delays[attempt])
            else:
                _logger.warning(
                    "Failed to publish event %s after %d attempts",
                    subject,
                    attempt + 1,
                )
