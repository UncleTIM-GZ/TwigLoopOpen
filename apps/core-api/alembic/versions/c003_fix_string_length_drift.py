"""Fix string length drift: application_source 32->50, decision_reason_code 64->100.

Aligns migration column lengths with model definitions in ProjectApplication.

Revision ID: c003
Revises: c002
"""

from alembic import op
import sqlalchemy as sa

revision = "c003"
down_revision = "c002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "project_applications",
        "application_source",
        type_=sa.String(50),
        existing_type=sa.String(32),
    )
    op.alter_column(
        "project_applications",
        "decision_reason_code",
        type_=sa.String(100),
        existing_type=sa.String(64),
    )


def downgrade() -> None:
    op.alter_column(
        "project_applications",
        "application_source",
        type_=sa.String(32),
        existing_type=sa.String(50),
    )
    op.alter_column(
        "project_applications",
        "decision_reason_code",
        type_=sa.String(64),
        existing_type=sa.String(100),
    )
