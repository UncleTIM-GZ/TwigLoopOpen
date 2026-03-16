"""create event tables: domain_events, state_transition_events, analytics_events

Revision ID: a003_event_tables
Revises: a002_incr_fields
Create Date: 2026-03-14

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a003_event_tables'
down_revision: str | Sequence[str] | None = 'a002_incr_fields'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create event tables with indexes."""
    # domain_events — aligned with DomainEvent ORM model
    op.create_table(
        'domain_events',
        sa.Column('event_type', sa.String(length=128), nullable=False),
        sa.Column('aggregate_type', sa.String(length=64), nullable=False),
        sa.Column('aggregate_id', sa.UUID(), nullable=False),
        sa.Column('actor_id', sa.UUID(), nullable=True),
        sa.Column('payload_json', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('correlation_id', sa.UUID(), nullable=True),
        sa.Column('causation_id', sa.UUID(), nullable=True),
        sa.Column('source_channel', sa.String(length=32), nullable=False, server_default='system'),
        sa.Column('schema_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_domain_events_aggregate', 'domain_events', ['aggregate_type', 'aggregate_id'])
    op.create_index('ix_domain_events_event_type', 'domain_events', ['event_type'])
    op.create_index('ix_domain_events_occurred_at', 'domain_events', ['occurred_at'])

    # state_transition_events — aligned with StateTransitionEvent ORM model
    op.create_table(
        'state_transition_events',
        sa.Column('object_type', sa.String(length=64), nullable=False),
        sa.Column('object_id', sa.UUID(), nullable=False),
        sa.Column('from_status', sa.String(length=64), nullable=True),
        sa.Column('to_status', sa.String(length=64), nullable=False),
        sa.Column('trigger_actor_id', sa.UUID(), nullable=True),
        sa.Column('trigger_reason', sa.String(length=128), nullable=True),
        sa.Column('source_event_id', sa.UUID(), nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_state_transition_events_object', 'state_transition_events', ['object_type', 'object_id'])

    # analytics_events — standalone, no ORM model yet
    op.create_table(
        'analytics_events',
        sa.Column('event_name', sa.String(length=128), nullable=False),
        sa.Column('actor_id', sa.UUID(), nullable=True),
        sa.Column('session_id', sa.String(length=128), nullable=True),
        sa.Column('project_id', sa.UUID(), nullable=True),
        sa.Column('task_id', sa.UUID(), nullable=True),
        sa.Column('payload_json', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_analytics_events_event_name', 'analytics_events', ['event_name'])
    op.create_index('ix_analytics_events_occurred_at', 'analytics_events', ['occurred_at'])


def downgrade() -> None:
    """Drop event tables and their indexes."""
    op.drop_index('ix_analytics_events_occurred_at', table_name='analytics_events')
    op.drop_index('ix_analytics_events_event_name', table_name='analytics_events')
    op.drop_table('analytics_events')

    op.drop_index('ix_state_transition_events_object', table_name='state_transition_events')
    op.drop_table('state_transition_events')

    op.drop_index('ix_domain_events_occurred_at', table_name='domain_events')
    op.drop_index('ix_domain_events_event_type', table_name='domain_events')
    op.drop_index('ix_domain_events_aggregate', table_name='domain_events')
    op.drop_table('domain_events')
