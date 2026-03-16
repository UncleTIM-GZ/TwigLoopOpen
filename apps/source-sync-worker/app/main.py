"""Source Sync Worker entrypoint.

Subscribes to NATS `source.webhook.received` events and processes
incoming GitHub webhook payloads by calling core-api.
"""

import asyncio
import json
import logging
import os
import signal
from types import FrameType

import httpx
from shared_config import AppSettings, NATSSettings
from shared_events import Subjects, connect_nats, disconnect_nats
from shared_observability import setup_telemetry

setup_telemetry(service_name="source-sync-worker")

_logger = logging.getLogger(__name__)
_settings = AppSettings()
_nats_settings = NATSSettings()

# core-api base URL
CORE_API_URL = os.getenv("CORE_API_BASE_URL", "http://localhost:8000")

_shutdown = asyncio.Event()


def _handle_signal(signum: int, frame: FrameType | None) -> None:
    _logger.info("Received signal %s, shutting down...", signum)
    _shutdown.set()


async def _process_webhook_event(data: dict[str, object]) -> None:
    """Process a single webhook event by logging it.

    The actual signal creation is handled by the webhook endpoint in core-api.
    This worker can perform additional async processing such as:
    - Fetching full commit diffs from GitHub API
    - Computing progress metrics
    - Triggering ClickHouse analytics writes
    """
    project_id = data.get("project_id")
    event_type = data.get("event_type")
    signal_id = data.get("signal_id")
    repo_url = data.get("repo_url")

    _logger.info(
        "Processing webhook: project=%s event=%s signal=%s repo=%s",
        project_id,
        event_type,
        signal_id,
        repo_url,
    )

    # Example: fetch additional data from GitHub API for enrichment
    # This is where the worker adds value beyond what the webhook handler does
    if event_type == "push" and repo_url:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Verify signal exists in core-api
                resp = await client.get(
                    f"{CORE_API_URL}/api/v1/projects/{project_id}/signals",
                    params={"limit": 1},
                )
                if resp.status_code == 200:
                    _logger.info("Signal verified in core-api for project %s", project_id)
            except httpx.HTTPError:
                _logger.warning("Failed to verify signal in core-api for project %s", project_id)


async def _subscribe_and_process() -> None:
    """Subscribe to NATS and process events until shutdown."""
    import nats

    nc = await nats.connect(_nats_settings.nats_url, connect_timeout=5)
    js = nc.jetstream()

    # Ensure stream exists
    import contextlib

    from nats.js.api import ConsumerConfig, StreamConfig
    from nats.js.errors import BadRequestError

    with contextlib.suppress(BadRequestError):
        await js.add_stream(StreamConfig(name="SOURCE", subjects=["source.>"]))

    # Create a durable pull subscription
    sub = await js.pull_subscribe(
        Subjects.SOURCE_WEBHOOK_RECEIVED,
        durable="source-sync-worker",
        config=ConsumerConfig(
            ack_wait=30,
            max_deliver=3,
        ),
    )

    _logger.info("Source sync worker started, listening for events...")

    while not _shutdown.is_set():
        try:
            msgs = await sub.fetch(batch=10, timeout=5)
            for msg in msgs:
                try:
                    data = json.loads(msg.data.decode())
                    payload = data.get("payload", data)
                    await _process_webhook_event(payload)
                    await msg.ack()
                except Exception:
                    _logger.exception("Failed to process message")
                    await msg.nak()
        except TimeoutError:
            # No messages available, just loop back
            continue
        except Exception:
            _logger.exception("Error fetching messages from NATS")
            await asyncio.sleep(1)

    await sub.unsubscribe()
    await nc.close()
    _logger.info("Source sync worker stopped.")


async def main() -> None:
    """Main entry point for the source sync worker."""
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    _logger.info("Starting source sync worker (env=%s)", _settings.environment)

    await connect_nats()
    try:
        await _subscribe_and_process()
    finally:
        await disconnect_nats()


if __name__ == "__main__":
    asyncio.run(main())
