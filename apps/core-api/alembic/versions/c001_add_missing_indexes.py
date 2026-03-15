"""add missing indexes from reliability scan

Revision ID: c001_add_missing_indexes
Revises: 0b3608505f7c
Create Date: 2026-03-15 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c001_add_missing_indexes'
down_revision: str | Sequence[str] | None = '0b3608505f7c'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add missing indexes identified in reliability scan."""
    # actors
    op.create_index('ix_actors_account_id', 'actors', ['account_id'])

    # projects
    op.create_index('ix_projects_founder_actor_id', 'projects', ['founder_actor_id'])
    op.create_index('ix_projects_status', 'projects', ['status'])
    op.create_index('ix_projects_project_type', 'projects', ['project_type'])
    op.create_index('ix_projects_created_at_desc', 'projects', [sa.text('created_at DESC')])

    # work_packages
    op.create_index('ix_work_packages_project_id', 'work_packages', ['project_id'])

    # task_cards
    op.create_index('ix_task_cards_work_package_id', 'task_cards', ['work_package_id'])

    # project_applications
    op.create_index('ix_applications_project_id', 'project_applications', ['project_id'])
    op.create_index('ix_applications_actor_id', 'project_applications', ['actor_id'])

    # project_seats
    op.create_index('ix_seats_project_id', 'project_seats', ['project_id'])

    # project_sources
    op.create_index('ix_sources_project_id', 'project_sources', ['project_id'])

    # project_signals
    op.create_index('ix_signals_project_occurred', 'project_signals', ['project_id', sa.text('occurred_at DESC')])

    # review_records
    op.create_index('ix_review_records_project_id', 'review_records', ['project_id'])

    # sponsor_supports
    op.create_index('ix_sponsor_supports_sponsor_id', 'sponsor_supports', ['sponsor_actor_id'])
    op.create_index('ix_sponsor_supports_project_id', 'sponsor_supports', ['project_id'])


def downgrade() -> None:
    """Drop all indexes in reverse order."""
    op.drop_index('ix_sponsor_supports_project_id')
    op.drop_index('ix_sponsor_supports_sponsor_id')
    op.drop_index('ix_review_records_project_id')
    op.drop_index('ix_signals_project_occurred')
    op.drop_index('ix_sources_project_id')
    op.drop_index('ix_seats_project_id')
    op.drop_index('ix_applications_actor_id')
    op.drop_index('ix_applications_project_id')
    op.drop_index('ix_task_cards_work_package_id')
    op.drop_index('ix_work_packages_project_id')
    op.drop_index('ix_projects_created_at_desc')
    op.drop_index('ix_projects_project_type')
    op.drop_index('ix_projects_status')
    op.drop_index('ix_projects_founder_actor_id')
    op.drop_index('ix_actors_account_id')
