"""add incremental fields to 12 existing tables per ERD

Revision ID: a002_incr_fields
Revises: a001_base_tables
Create Date: 2026-03-14

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a002_incr_fields'
down_revision: str | Sequence[str] | None = 'a001_base_tables'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add incremental columns to 12 tables."""
    # --- accounts ---
    op.add_column('accounts', sa.Column('primary_actor_id', sa.UUID(), nullable=True))
    op.add_column('accounts', sa.Column(
        'account_flags_json', postgresql.JSONB(astext_type=sa.Text()),
        server_default='{}', nullable=False,
    ))
    op.add_column('accounts', sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=True))

    # --- actors ---
    op.add_column('actors', sa.Column('feature_snapshot_version', sa.Integer(), server_default='1', nullable=False))
    op.add_column('actors', sa.Column('last_feature_computed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('actors', sa.Column('dominant_project_type', sa.String(length=64), nullable=True))
    op.add_column('actors', sa.Column('dominant_task_type', sa.String(length=64), nullable=True))
    op.add_column('actors', sa.Column('reuse_count', sa.Integer(), server_default='0', nullable=False))
    op.add_column('actors', sa.Column('completion_rate', sa.Numeric(precision=6, scale=4), nullable=True))
    op.add_column('actors', sa.Column('collaboration_breadth', sa.Integer(), server_default='0', nullable=False))
    op.add_column('actors', sa.Column('coordination_load_score', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('actors', sa.Column('structural_role_label', sa.String(length=64), nullable=True))

    # --- projects ---
    op.add_column('projects', sa.Column('feature_snapshot_version', sa.Integer(), server_default='1', nullable=False))
    op.add_column('projects', sa.Column('last_feature_computed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('projects', sa.Column('task_count', sa.Integer(), server_default='0', nullable=False))
    op.add_column('projects', sa.Column('avg_ewu', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('projects', sa.Column('max_ewu', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('projects', sa.Column('dependency_density', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('projects', sa.Column('role_diversity_score', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('projects', sa.Column('start_pattern', sa.String(length=128), nullable=True))
    op.add_column('projects', sa.Column('project_complexity_score', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('projects', sa.Column('structural_cluster_id', sa.String(length=64), nullable=True))

    # --- work_packages ---
    op.add_column('work_packages', sa.Column('task_count', sa.Integer(), server_default='0', nullable=False))
    op.add_column('work_packages', sa.Column('avg_ewu', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('work_packages', sa.Column('dependency_density', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('work_packages', sa.Column('main_task_type', sa.String(length=64), nullable=True))
    op.add_column('work_packages', sa.Column('main_role_needed', sa.String(length=64), nullable=True))
    op.add_column('work_packages', sa.Column('feature_snapshot_version', sa.Integer(), server_default='1', nullable=False))

    # --- task_cards ---
    op.add_column('task_cards', sa.Column('raw_goal', sa.Text(), nullable=True))
    op.add_column('task_cards', sa.Column('raw_output_spec', sa.Text(), nullable=True))
    op.add_column('task_cards', sa.Column('raw_completion_criteria', sa.Text(), nullable=True))
    op.add_column('task_cards', sa.Column('normalized_goal', sa.Text(), nullable=True))
    op.add_column('task_cards', sa.Column('normalized_output_spec', sa.Text(), nullable=True))
    op.add_column('task_cards', sa.Column('normalized_completion_criteria', sa.Text(), nullable=True))
    op.add_column('task_cards', sa.Column('criticality_score', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('task_cards', sa.Column('collaboration_complexity_score', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('task_cards', sa.Column('feature_snapshot_version', sa.Integer(), server_default='1', nullable=False))
    op.add_column('task_cards', sa.Column('last_feature_computed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('task_cards', sa.Column('graph_exportable', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('task_cards', sa.Column('structural_role_hint', sa.String(length=64), nullable=True))

    # --- project_applications ---
    op.add_column('project_applications', sa.Column('application_source', sa.String(length=32), nullable=True))
    op.add_column('project_applications', sa.Column('match_score_rule', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('project_applications', sa.Column('match_score_signal', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('project_applications', sa.Column('match_score_structural', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('project_applications', sa.Column('final_match_score', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('project_applications', sa.Column('decision_reason_code', sa.String(length=64), nullable=True))

    # --- project_seats ---
    op.add_column('project_seats', sa.Column('seat_rank', sa.Integer(), nullable=True))
    op.add_column('project_seats', sa.Column('seat_goal', sa.Text(), nullable=True))
    op.add_column('project_seats', sa.Column('seat_dependency_note', sa.Text(), nullable=True))
    op.add_column('project_seats', sa.Column('structural_importance_score', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('project_seats', sa.Column('entered_via_application_id', sa.UUID(), nullable=True))

    # --- task_assignments ---
    op.add_column('task_assignments', sa.Column('assignment_source', sa.String(length=32), nullable=True))
    op.add_column('task_assignments', sa.Column('is_trial_assignment', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('task_assignments', sa.Column('effort_estimate', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('task_assignments', sa.Column('effort_actual', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('task_assignments', sa.Column('rework_count', sa.Integer(), server_default='0', nullable=False))

    # --- project_signals ---
    op.add_column('project_signals', sa.Column('normalized_signal_weight', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('project_signals', sa.Column('signal_group', sa.String(length=64), nullable=True))
    op.add_column('project_signals', sa.Column('derived_from_event_id', sa.UUID(), nullable=True))
    op.add_column('project_signals', sa.Column('is_structural_signal', sa.Boolean(), server_default='false', nullable=False))

    # --- review_records ---
    op.add_column('review_records', sa.Column('review_scope', sa.String(length=64), nullable=True))
    op.add_column('review_records', sa.Column('review_complexity_score', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('review_records', sa.Column('review_cycle_index', sa.Integer(), server_default='1', nullable=False))
    op.add_column('review_records', sa.Column('source_event_id', sa.UUID(), nullable=True))

    # --- sponsor_supports ---
    op.add_column('sponsor_supports', sa.Column('support_goal', sa.Text(), nullable=True))
    op.add_column('sponsor_supports', sa.Column('target_structure_type', sa.String(length=64), nullable=True))
    op.add_column('sponsor_supports', sa.Column('support_effectiveness_score', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('sponsor_supports', sa.Column('consumed_units', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('sponsor_supports', sa.Column('source_event_id', sa.UUID(), nullable=True))

    # --- verifiable_credentials ---
    op.add_column('verifiable_credentials', sa.Column('credential_version', sa.Integer(), server_default='1', nullable=False))
    op.add_column('verifiable_credentials', sa.Column('credential_source_event_id', sa.UUID(), nullable=True))
    op.add_column('verifiable_credentials', sa.Column('credential_source_relation_id', sa.UUID(), nullable=True))
    op.add_column('verifiable_credentials', sa.Column('feature_snapshot_version', sa.Integer(), server_default='1', nullable=False))


def downgrade() -> None:
    """Drop all incremental columns in reverse order."""
    # --- verifiable_credentials ---
    op.drop_column('verifiable_credentials', 'feature_snapshot_version')
    op.drop_column('verifiable_credentials', 'credential_source_relation_id')
    op.drop_column('verifiable_credentials', 'credential_source_event_id')
    op.drop_column('verifiable_credentials', 'credential_version')

    # --- sponsor_supports ---
    op.drop_column('sponsor_supports', 'source_event_id')
    op.drop_column('sponsor_supports', 'consumed_units')
    op.drop_column('sponsor_supports', 'support_effectiveness_score')
    op.drop_column('sponsor_supports', 'target_structure_type')
    op.drop_column('sponsor_supports', 'support_goal')

    # --- review_records ---
    op.drop_column('review_records', 'source_event_id')
    op.drop_column('review_records', 'review_cycle_index')
    op.drop_column('review_records', 'review_complexity_score')
    op.drop_column('review_records', 'review_scope')

    # --- project_signals ---
    op.drop_column('project_signals', 'is_structural_signal')
    op.drop_column('project_signals', 'derived_from_event_id')
    op.drop_column('project_signals', 'signal_group')
    op.drop_column('project_signals', 'normalized_signal_weight')

    # --- task_assignments ---
    op.drop_column('task_assignments', 'rework_count')
    op.drop_column('task_assignments', 'effort_actual')
    op.drop_column('task_assignments', 'effort_estimate')
    op.drop_column('task_assignments', 'is_trial_assignment')
    op.drop_column('task_assignments', 'assignment_source')

    # --- project_seats ---
    op.drop_column('project_seats', 'entered_via_application_id')
    op.drop_column('project_seats', 'structural_importance_score')
    op.drop_column('project_seats', 'seat_dependency_note')
    op.drop_column('project_seats', 'seat_goal')
    op.drop_column('project_seats', 'seat_rank')

    # --- project_applications ---
    op.drop_column('project_applications', 'decision_reason_code')
    op.drop_column('project_applications', 'final_match_score')
    op.drop_column('project_applications', 'match_score_structural')
    op.drop_column('project_applications', 'match_score_signal')
    op.drop_column('project_applications', 'match_score_rule')
    op.drop_column('project_applications', 'application_source')

    # --- task_cards ---
    op.drop_column('task_cards', 'structural_role_hint')
    op.drop_column('task_cards', 'graph_exportable')
    op.drop_column('task_cards', 'last_feature_computed_at')
    op.drop_column('task_cards', 'feature_snapshot_version')
    op.drop_column('task_cards', 'collaboration_complexity_score')
    op.drop_column('task_cards', 'criticality_score')
    op.drop_column('task_cards', 'normalized_completion_criteria')
    op.drop_column('task_cards', 'normalized_output_spec')
    op.drop_column('task_cards', 'normalized_goal')
    op.drop_column('task_cards', 'raw_completion_criteria')
    op.drop_column('task_cards', 'raw_output_spec')
    op.drop_column('task_cards', 'raw_goal')

    # --- work_packages ---
    op.drop_column('work_packages', 'feature_snapshot_version')
    op.drop_column('work_packages', 'main_role_needed')
    op.drop_column('work_packages', 'main_task_type')
    op.drop_column('work_packages', 'dependency_density')
    op.drop_column('work_packages', 'avg_ewu')
    op.drop_column('work_packages', 'task_count')

    # --- projects ---
    op.drop_column('projects', 'structural_cluster_id')
    op.drop_column('projects', 'project_complexity_score')
    op.drop_column('projects', 'start_pattern')
    op.drop_column('projects', 'role_diversity_score')
    op.drop_column('projects', 'dependency_density')
    op.drop_column('projects', 'max_ewu')
    op.drop_column('projects', 'avg_ewu')
    op.drop_column('projects', 'task_count')
    op.drop_column('projects', 'last_feature_computed_at')
    op.drop_column('projects', 'feature_snapshot_version')

    # --- actors ---
    op.drop_column('actors', 'structural_role_label')
    op.drop_column('actors', 'coordination_load_score')
    op.drop_column('actors', 'collaboration_breadth')
    op.drop_column('actors', 'completion_rate')
    op.drop_column('actors', 'reuse_count')
    op.drop_column('actors', 'dominant_task_type')
    op.drop_column('actors', 'dominant_project_type')
    op.drop_column('actors', 'last_feature_computed_at')
    op.drop_column('actors', 'feature_snapshot_version')

    # --- accounts ---
    op.drop_column('accounts', 'last_active_at')
    op.drop_column('accounts', 'account_flags_json')
    op.drop_column('accounts', 'primary_actor_id')
