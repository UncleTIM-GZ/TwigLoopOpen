"""Shared schemas used across multiple workflow domains."""

from dataclasses import dataclass


@dataclass
class PublishEventInput:
    event_type: str
    entity_id: str
