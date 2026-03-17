"""Add GitHub signal reserved fields to task_cards.

Revision ID: d002
Revises: d001
"""

from alembic import op
import sqlalchemy as sa

revision = "d002"
down_revision = "d001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("task_cards", sa.Column("repo_url", sa.String(500), nullable=True))
    op.add_column("task_cards", sa.Column("branch_name", sa.String(255), nullable=True))
    op.add_column("task_cards", sa.Column("pr_url", sa.String(500), nullable=True))
    op.add_column(
        "task_cards", sa.Column("latest_commit_sha", sa.String(64), nullable=True)
    )
    op.add_column(
        "task_cards",
        sa.Column("signal_count", sa.Integer, nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("task_cards", "signal_count")
    op.drop_column("task_cards", "latest_commit_sha")
    op.drop_column("task_cards", "pr_url")
    op.drop_column("task_cards", "branch_name")
    op.drop_column("task_cards", "repo_url")
