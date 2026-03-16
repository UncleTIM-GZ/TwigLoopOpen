"""create drafts table

Revision ID: b001
Revises: 0b3608505f7c
Create Date: 2026-03-15

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b001"
down_revision: str | Sequence[str] | None = "a006_updated_at_trigger"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "drafts",
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("draft_type", sa.String(length=64), nullable=False),
        sa.Column(
            "source_channel",
            sa.String(length=32),
            nullable=False,
            server_default="mcp",
        ),
        sa.Column(
            "collected_fields_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "missing_fields_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "warnings_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "preflight_status",
            sa.String(length=32),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "preflight_result_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("last_llm_summary", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default="collecting",
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_id"], ["actors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_drafts_actor_id", "drafts", ["actor_id"])
    op.create_index("ix_drafts_status", "drafts", ["status"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_drafts_status", table_name="drafts")
    op.drop_index("ix_drafts_actor_id", table_name="drafts")
    op.drop_table("drafts")
