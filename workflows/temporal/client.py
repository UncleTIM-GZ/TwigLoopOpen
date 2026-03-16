"""Temporal client factory."""

import asyncio

from shared_config import TemporalSettings
from temporalio.client import Client

_settings = TemporalSettings()


async def get_temporal_client() -> Client:
    """Create a Temporal client connected to the configured server."""
    return await asyncio.wait_for(
        Client.connect(
            _settings.temporal_host,
            namespace=_settings.temporal_namespace,
        ),
        timeout=10.0,
    )
