"""Add unique constraint on project_seats (project_id, actor_id).

Prevents duplicate seats from concurrent accept operations.

Revision ID: c002
Revises: c001
"""

from alembic import op

revision = "c002"
down_revision = "c001_add_missing_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_project_seats_project_actor",
        "project_seats",
        ["project_id", "actor_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_project_seats_project_actor", "project_seats", type_="unique")
