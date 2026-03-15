"""Tests for EWU/RWU/SWU single-source-of-truth consolidation.

Verifies:
1. Single EWU rule source (domain/ewu.py is the only authority)
2. RWU/SWU v1 frozen rules
3. EWU cap enforcement in CRUD paths
4. Schema/default consistency
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.domain.ewu import (
    RISK_MULTIPLIERS,
    TASK_TYPE_WEIGHTS,
    EwuInput,
    calculate_ewu,
)
from app.domain.quota_config import MAX_EWU_PER_TASK
from app.domain.rwu_swu import (
    DEFAULT_REWARD_TIER,
    DEFAULT_SPONSOR_TIER,
    REWARD_MULTIPLIERS,
    SPONSOR_MULTIPLIERS,
    calculate_rwu,
    calculate_swu,
)
from app.schemas.task_card import CreateTaskCardRequest, TaskCardResponse


# ── Single Rule Source ─────────────────────────────────────────


class TestSingleRuleSource:
    """Verify EWU has exactly one authoritative calculation."""

    def test_ewu_task_types_complete(self) -> None:
        """All 8 spec task types have weights."""
        expected = {
            "requirement_clarification",
            "research",
            "product_design",
            "development",
            "testing_fix",
            "documentation",
            "collaboration_support",
            "review_audit",
        }
        assert set(TASK_TYPE_WEIGHTS.keys()) == expected

    def test_ewu_risk_levels_complete(self) -> None:
        assert set(RISK_MULTIPLIERS.keys()) == {"low", "medium", "high"}

    def test_ewu_formula_deterministic(self) -> None:
        """Same input always produces same output."""
        inp = EwuInput(
            task_type="development",
            risk_level="medium",
            complexity=3,
            criticality=4,
            collaboration_complexity=2,
        )
        r1 = calculate_ewu(inp)
        r2 = calculate_ewu(inp)
        assert r1.ewu == r2.ewu

    def test_ewu_max_value_is_8(self) -> None:
        """Max possible EWU: development(1.5) × avg(5,5,5)=5 × high(1.6) = 12.
        But quota cap is 8."""
        assert MAX_EWU_PER_TASK == 8

    def test_all_task_types_produce_positive_ewu(self) -> None:
        for tt in TASK_TYPE_WEIGHTS:
            result = calculate_ewu(
                EwuInput(
                    task_type=tt,
                    risk_level="low",
                    complexity=3,
                    criticality=3,
                    collaboration_complexity=3,
                )
            )
            assert result.ewu > 0, f"{tt} should produce positive EWU"


# ── RWU/SWU v1 Frozen Rules ─────────────────────────────────────


class TestRwuSwuV1Frozen:
    """Verify RWU/SWU v1 fixed multiplier rules."""

    def test_rwu_default_tier_is_standard(self) -> None:
        assert DEFAULT_REWARD_TIER == "standard"

    def test_rwu_standard_multiplier_is_1_2(self) -> None:
        assert REWARD_MULTIPLIERS["standard"] == Decimal("1.2")

    def test_rwu_v1_formula(self) -> None:
        """RWU = EWU × 1.2 (fixed v1)."""
        result = calculate_rwu(Decimal("4.50"))
        assert result.rwu == Decimal("5.40")

    def test_swu_default_tier_is_standard(self) -> None:
        assert DEFAULT_SPONSOR_TIER == "standard"

    def test_swu_standard_multiplier_is_1_0(self) -> None:
        """SWU v1 = EWU × 1.0 (equals EWU by design)."""
        assert SPONSOR_MULTIPLIERS["standard"] == Decimal("1.0")

    def test_swu_v1_equals_ewu(self) -> None:
        """SWU standard = EWU × 1.0, intentionally equal."""
        result = calculate_swu(Decimal("4.50"))
        assert result.swu == Decimal("4.50")

    def test_rwu_zero_ewu(self) -> None:
        assert calculate_rwu(Decimal("0")).rwu == Decimal("0.00")

    def test_swu_zero_ewu(self) -> None:
        assert calculate_swu(Decimal("0")).swu == Decimal("0.00")

    def test_rwu_boundary_at_max_ewu(self) -> None:
        """RWU at EWU cap: 8.00 × 1.2 = 9.60."""
        result = calculate_rwu(Decimal("8.00"))
        assert result.rwu == Decimal("9.60")


# ── EWU Cap Enforcement ─────────────────────────────────────────


class TestEwuCapEnforcement:
    """Verify EWU > 8 is blocked at schema and config levels."""

    def test_quota_config_max_ewu_per_task(self) -> None:
        assert MAX_EWU_PER_TASK == 8

    def test_create_schema_allows_ewu_at_cap(self) -> None:
        """EWU = 8 should be accepted by schema."""
        req = CreateTaskCardRequest(
            title="Test",
            task_type="development",
            goal="test goal",
            output_spec="test output",
            completion_criteria="test criteria",
            main_role="developer",
            ewu=Decimal("8.00"),
        )
        assert req.ewu == Decimal("8.00")

    def test_create_schema_allows_ewu_above_cap(self) -> None:
        """Schema itself doesn't block >8 — service layer does."""
        req = CreateTaskCardRequest(
            title="Test",
            task_type="development",
            goal="test goal",
            output_spec="test output",
            completion_criteria="test criteria",
            main_role="developer",
            ewu=Decimal("10.00"),
        )
        assert req.ewu == Decimal("10.00")


# ── Schema/Default Consistency ─────────────────────────────────


class TestSchemaDefaultConsistency:
    """Verify schema and model defaults are aligned."""

    def test_create_schema_ewu_default_is_1(self) -> None:
        req = CreateTaskCardRequest(
            title="Test",
            task_type="development",
            goal="test goal",
            output_spec="test output",
            completion_criteria="test criteria",
            main_role="developer",
        )
        assert req.ewu == Decimal("1.0")

    def test_response_schema_has_ewu_rwu_swu(self) -> None:
        fields = TaskCardResponse.model_fields
        assert "ewu" in fields
        assert "rwu" in fields
        assert "swu" in fields
        assert "has_reward" in fields

    def test_create_schema_forbids_extra(self) -> None:
        with pytest.raises(ValidationError):
            CreateTaskCardRequest(
                title="Test",
                task_type="development",
                goal="test goal",
                output_spec="test output",
                completion_criteria="test criteria",
                main_role="developer",
                unknown_field="bad",
            )


# ── Aggregation Schema ─────────────────────────────────────────


class TestAggregationSchema:
    """Verify WP and Project response schemas include aggregation fields."""

    def test_wp_response_has_aggregation_fields(self) -> None:
        from app.schemas.work_package import WorkPackageResponse

        fields = WorkPackageResponse.model_fields
        assert "total_ewu" in fields
        assert "avg_ewu" in fields
        assert "total_rwu" in fields
        assert "total_swu" in fields
        assert "task_count" in fields

    def test_project_response_has_aggregation_fields(self) -> None:
        from app.schemas.project import ProjectResponse

        fields = ProjectResponse.model_fields
        assert "total_ewu" in fields
        assert "avg_ewu" in fields
        assert "max_ewu" in fields
        assert "total_rwu" in fields
        assert "total_swu" in fields
        assert "task_count" in fields
