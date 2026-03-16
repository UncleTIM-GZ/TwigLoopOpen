"""Add delivery_evidences, task_verifications tables and evidence fields.

Creates the delivery evidence and task verification tables, adds
verification/completion fields to task_cards, and evidence-backed
issuance fields to verifiable_credentials.

Revision ID: d001
Revises: c003
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "d001"
down_revision = "c003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- delivery_evidences table ---
    op.create_table(
        "delivery_evidences",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("task_cards.id"), nullable=False),
        sa.Column("actor_id", UUID(as_uuid=True), sa.ForeignKey("actors.id"), nullable=False),
        sa.Column("evidence_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("evidence_url", sa.String(500), nullable=False),
        sa.Column("evidence_source", sa.String(50), nullable=False, server_default="manual"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_latest", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("status", sa.String(50), nullable=False, server_default="submitted"),
        sa.Column("reviewer_note", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_delivery_evidences_task_id", "delivery_evidences", ["task_id"])
    op.create_index("ix_delivery_evidences_actor_id", "delivery_evidences", ["actor_id"])

    # --- task_verifications table ---
    op.create_table(
        "task_verifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("task_cards.id"), nullable=False),
        sa.Column(
            "evidence_id",
            UUID(as_uuid=True),
            sa.ForeignKey("delivery_evidences.id"),
            nullable=True,
        ),
        sa.Column("reviewer_id", UUID(as_uuid=True), sa.ForeignKey("actors.id"), nullable=False),
        sa.Column("decision", sa.String(50), nullable=False),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_task_verifications_task_id", "task_verifications", ["task_id"])

    # --- ALTER task_cards: add verification / completion fields ---
    op.add_column(
        "task_cards",
        sa.Column(
            "verification_status", sa.String(50), nullable=False, server_default="unverified"
        ),
    )
    op.add_column(
        "task_cards",
        sa.Column(
            "completion_mode", sa.String(50), nullable=False, server_default="evidence_backed"
        ),
    )
    op.add_column(
        "task_cards",
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "task_cards",
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "task_cards",
        sa.Column("verified_by", UUID(as_uuid=True), nullable=True),
    )

    # --- ALTER verifiable_credentials: add evidence-backed issuance fields ---
    op.add_column(
        "verifiable_credentials",
        sa.Column(
            "evidence_id",
            UUID(as_uuid=True),
            sa.ForeignKey("delivery_evidences.id"),
            nullable=True,
        ),
    )
    op.add_column(
        "verifiable_credentials",
        sa.Column(
            "verification_id",
            UUID(as_uuid=True),
            sa.ForeignKey("task_verifications.id"),
            nullable=True,
        ),
    )
    op.add_column(
        "verifiable_credentials",
        sa.Column("issuance_basis", sa.String(50), nullable=False, server_default="verified"),
    )

    # --- Backfill existing completed tasks as legacy ---
    op.execute(
        "UPDATE task_cards SET completion_mode = 'legacy' WHERE status = 'completed'"
    )
    # --- Backfill existing VCs as legacy ---
    op.execute(
        "UPDATE verifiable_credentials SET issuance_basis = 'legacy'"
    )


def downgrade() -> None:
    # --- Remove verifiable_credentials columns ---
    op.drop_column("verifiable_credentials", "issuance_basis")
    op.drop_column("verifiable_credentials", "verification_id")
    op.drop_column("verifiable_credentials", "evidence_id")

    # --- Remove task_cards columns ---
    op.drop_column("task_cards", "verified_by")
    op.drop_column("task_cards", "verified_at")
    op.drop_column("task_cards", "submitted_at")
    op.drop_column("task_cards", "completion_mode")
    op.drop_column("task_cards", "verification_status")

    # --- Drop tables ---
    op.drop_index("ix_task_verifications_task_id", "task_verifications")
    op.drop_table("task_verifications")
    op.drop_index("ix_delivery_evidences_actor_id", "delivery_evidences")
    op.drop_index("ix_delivery_evidences_task_id", "delivery_evidences")
    op.drop_table("delivery_evidences")
