"""create edge tables: actor_project_edges, actor_actor_edges

Revision ID: a004_edge_tables
Revises: a003_event_tables
Create Date: 2026-03-14

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a004_edge_tables'
down_revision: str | Sequence[str] | None = 'a003_event_tables'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create edge tables aligned with ORM models."""
    # actor_project_edges — aligned with ActorProjectEdge ORM
    op.create_table(
        'actor_project_edges',
        sa.Column('actor_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('edge_type', sa.String(length=64), nullable=False),
        sa.Column('weight', sa.Numeric(precision=10, scale=2), nullable=False, server_default='1.0'),
        sa.Column('confidence', sa.Numeric(precision=10, scale=2), nullable=False, server_default='1.0'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='active'),
        sa.Column('valid_from', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('valid_to', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source_event_id', sa.UUID(), nullable=True),
        sa.Column('source_object_type', sa.String(length=64), nullable=True),
        sa.Column('source_object_id', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['actors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_actor_project_edges_actor_id', 'actor_project_edges', ['actor_id'])
    op.create_index('ix_actor_project_edges_project_id', 'actor_project_edges', ['project_id'])
    op.create_index('ix_actor_project_edges_edge_type', 'actor_project_edges', ['edge_type'])

    # actor_actor_edges — aligned with ActorActorEdge ORM
    op.create_table(
        'actor_actor_edges',
        sa.Column('actor_a_id', sa.UUID(), nullable=False),
        sa.Column('actor_b_id', sa.UUID(), nullable=False),
        sa.Column('edge_type', sa.String(length=64), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=True),
        sa.Column('task_id', sa.UUID(), nullable=True),
        sa.Column('weight', sa.Numeric(precision=10, scale=2), nullable=False, server_default='1.0'),
        sa.Column('confidence', sa.Numeric(precision=10, scale=2), nullable=False, server_default='1.0'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='active'),
        sa.Column('valid_from', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('valid_to', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source_event_id', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['actor_a_id'], ['actors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_b_id'], ['actors.id'], ondelete='CASCADE'),
        sa.CheckConstraint('actor_a_id <> actor_b_id', name='ck_actor_actor_edges_no_self_loop'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_actor_actor_edges_actor_a_id', 'actor_actor_edges', ['actor_a_id'])
    op.create_index('ix_actor_actor_edges_actor_b_id', 'actor_actor_edges', ['actor_b_id'])
    op.create_index('ix_actor_actor_edges_edge_type', 'actor_actor_edges', ['edge_type'])


def downgrade() -> None:
    """Drop edge tables and their indexes."""
    op.drop_index('ix_actor_actor_edges_edge_type', table_name='actor_actor_edges')
    op.drop_index('ix_actor_actor_edges_actor_b_id', table_name='actor_actor_edges')
    op.drop_index('ix_actor_actor_edges_actor_a_id', table_name='actor_actor_edges')
    op.drop_table('actor_actor_edges')

    op.drop_index('ix_actor_project_edges_edge_type', table_name='actor_project_edges')
    op.drop_index('ix_actor_project_edges_project_id', table_name='actor_project_edges')
    op.drop_index('ix_actor_project_edges_actor_id', table_name='actor_project_edges')
    op.drop_table('actor_project_edges')
