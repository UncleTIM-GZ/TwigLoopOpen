"""add missing base tables: task_assignments, review_records, sponsor_supports, verifiable_credentials

Revision ID: a001_base_tables
Revises: 0b3608505f7c
Create Date: 2026-03-14

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a001_base_tables'
down_revision: str | Sequence[str] | None = '0b3608505f7c'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create 4 missing base tables from ERD."""
    op.create_table(
        'task_assignments',
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('actor_id', sa.UUID(), nullable=False),
        sa.Column('seat_id', sa.UUID(), nullable=False),
        sa.Column('assigned_by', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='pending', nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['task_cards.id']),
        sa.ForeignKeyConstraint(['actor_id'], ['actors.id']),
        sa.ForeignKeyConstraint(['seat_id'], ['project_seats.id']),
        sa.ForeignKeyConstraint(['assigned_by'], ['actors.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'review_records',
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('reviewer_actor_id', sa.UUID(), nullable=False),
        sa.Column('milestone', sa.String(length=128), nullable=False),
        sa.Column('decision', sa.String(length=50), nullable=False),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['reviewer_actor_id'], ['actors.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'sponsor_supports',
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('sponsor_actor_id', sa.UUID(), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=True),
        sa.Column('support_type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='active', nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['sponsor_actor_id'], ['actors.id']),
        sa.ForeignKeyConstraint(['task_id'], ['task_cards.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'verifiable_credentials',
        sa.Column('actor_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=True),
        sa.Column('task_id', sa.UUID(), nullable=True),
        sa.Column('credential_type', sa.String(length=100), nullable=False),
        sa.Column('credential_data_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='draft', nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['actors.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['task_id'], ['task_cards.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Drop 4 base tables in reverse order."""
    op.drop_table('verifiable_credentials')
    op.drop_table('sponsor_supports')
    op.drop_table('review_records')
    op.drop_table('task_assignments')
