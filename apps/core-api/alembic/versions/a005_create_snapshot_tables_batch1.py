"""create snapshot tables: actor_feature_snapshots, project_feature_snapshots

Revision ID: a005_snapshot_tables
Revises: a004_edge_tables
Create Date: 2026-03-14

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a005_snapshot_tables'
down_revision: str | Sequence[str] | None = 'a004_edge_tables'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create feature snapshot tables aligned with ORM models."""
    # actor_feature_snapshots — aligned with ActorFeatureSnapshot ORM
    op.create_table(
        'actor_feature_snapshots',
        sa.Column('actor_id', sa.UUID(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('dominant_project_type', sa.String(length=64), nullable=True),
        sa.Column('dominant_task_type', sa.String(length=64), nullable=True),
        sa.Column('completion_rate', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('reuse_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('collaboration_breadth', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('coordination_load_score', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('public_benefit_participation_score', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('review_reliability_score', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('feature_json', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['actors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_actor_feature_snapshots_actor_computed',
        'actor_feature_snapshots',
        ['actor_id', sa.text('computed_at DESC')],
    )

    # project_feature_snapshots — aligned with ProjectFeatureSnapshot ORM
    op.create_table(
        'project_feature_snapshots',
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('task_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_ewu', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('max_ewu', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('dependency_density', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('role_diversity_score', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('start_pattern', sa.String(length=128), nullable=True),
        sa.Column('project_complexity_score', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('feature_json', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_project_feature_snapshots_project_computed',
        'project_feature_snapshots',
        ['project_id', sa.text('computed_at DESC')],
    )


def downgrade() -> None:
    """Drop snapshot tables and their indexes."""
    op.drop_index('ix_project_feature_snapshots_project_computed', table_name='project_feature_snapshots')
    op.drop_table('project_feature_snapshots')

    op.drop_index('ix_actor_feature_snapshots_actor_computed', table_name='actor_feature_snapshots')
    op.drop_table('actor_feature_snapshots')
