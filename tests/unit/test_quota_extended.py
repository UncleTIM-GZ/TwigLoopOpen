"""Tests for quota / preflight / EWU extended scenarios.

Covers: EWU task_type weights, risk_level multipliers, RWU/SWU calculation,
quota limit constants, and EWU cap gate enforcement.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.domain.ewu import (
    RISK_MULTIPLIERS,
    TASK_TYPE_WEIGHTS,
    EwuInput,
    EwuResult,
    calculate_ewu,
)
from app.domain.quota_config import (
    ACTIVE_PROJECT_STATUSES,
    ACTIVE_TASK_STATUSES,
    MAX_ACTIVE_PROJECTS_NEW_FOUNDER,
    MAX_ACTIVE_TASKS_DEFAULT,
    MAX_EWU_PER_TASK,
    MAX_OPEN_SEATS_DEFAULT,
    MAX_PENDING_APPLICATIONS_PER_PROJECT,
    MAX_PENDING_APPLICATIONS_PER_TASK,
    MAX_TASKS_PER_PROJECT,
    MAX_TASKS_PER_WORK_PACKAGE,
    MAX_WORK_PACKAGES_PER_PROJECT,
    OPEN_SEAT_STATUSES,
    PENDING_APPLICATION_STATUSES,
)
from app.domain.rwu_swu import (
    DEFAULT_REWARD_TIER,
    DEFAULT_SPONSOR_TIER,
    REWARD_MULTIPLIERS,
    SPONSOR_MULTIPLIERS,
    RwuResult,
    SwuResult,
    calculate_rwu,
    calculate_swu,
)


# ── EWU task_type weights ────────────────────────────────────────────


class TestEwuTaskTypeWeights:
    def test_requirement_clarification_weight(self) -> None:
        assert TASK_TYPE_WEIGHTS["requirement_clarification"] == Decimal("0.8")

    def test_research_weight(self) -> None:
        assert TASK_TYPE_WEIGHTS["research"] == Decimal("1.0")

    def test_product_design_weight(self) -> None:
        assert TASK_TYPE_WEIGHTS["product_design"] == Decimal("1.2")

    def test_development_weight(self) -> None:
        assert TASK_TYPE_WEIGHTS["development"] == Decimal("1.5")

    def test_testing_fix_weight(self) -> None:
        assert TASK_TYPE_WEIGHTS["testing_fix"] == Decimal("1.0")

    def test_documentation_weight(self) -> None:
        assert TASK_TYPE_WEIGHTS["documentation"] == Decimal("0.7")

    def test_collaboration_support_weight(self) -> None:
        assert TASK_TYPE_WEIGHTS["collaboration_support"] == Decimal("0.6")

    def test_review_audit_weight(self) -> None:
        assert TASK_TYPE_WEIGHTS["review_audit"] == Decimal("0.9")


# ── EWU risk_level multipliers ───────────────────────────────────────


class TestEwuRiskMultipliers:
    def test_low_multiplier(self) -> None:
        assert RISK_MULTIPLIERS["low"] == Decimal("1.0")

    def test_medium_multiplier(self) -> None:
        assert RISK_MULTIPLIERS["medium"] == Decimal("1.3")

    def test_high_multiplier(self) -> None:
        assert RISK_MULTIPLIERS["high"] == Decimal("1.6")

    def test_exactly_three_risk_levels(self) -> None:
        assert len(RISK_MULTIPLIERS) == 3

    def test_all_multipliers_are_positive(self) -> None:
        for level, mult in RISK_MULTIPLIERS.items():
            assert mult > 0, f"Multiplier for '{level}' should be positive"


# ── RWU calculation ──────────────────────────────────────────────────


class TestRwuCalculation:
    def test_standard_tier_1_2x(self) -> None:
        result = calculate_rwu(Decimal("3.00"))
        assert result.rwu == Decimal("3.60")

    def test_urgent_tier_1_5x(self) -> None:
        result = calculate_rwu(Decimal("3.00"), "urgent")
        assert result.rwu == Decimal("4.50")

    def test_premium_tier_2_0x(self) -> None:
        result = calculate_rwu(Decimal("3.00"), "premium")
        assert result.rwu == Decimal("6.00")

    def test_rwu_result_is_rwu_result_type(self) -> None:
        result = calculate_rwu(Decimal("1.00"))
        assert isinstance(result, RwuResult)

    def test_rwu_breakdown_contains_tier(self) -> None:
        result = calculate_rwu(Decimal("2.00"), "urgent")
        assert "urgent" in result.breakdown


# ── SWU calculation ──────────────────────────────────────────────────


class TestSwuCalculation:
    def test_standard_tier_1_0x(self) -> None:
        result = calculate_swu(Decimal("3.00"))
        assert result.swu == Decimal("3.00")

    def test_matched_tier_1_5x(self) -> None:
        result = calculate_swu(Decimal("3.00"), "matched")
        assert result.swu == Decimal("4.50")

    def test_impact_tier_2_0x(self) -> None:
        result = calculate_swu(Decimal("3.00"), "impact")
        assert result.swu == Decimal("6.00")

    def test_swu_result_is_swu_result_type(self) -> None:
        result = calculate_swu(Decimal("1.00"))
        assert isinstance(result, SwuResult)

    def test_swu_breakdown_contains_tier(self) -> None:
        result = calculate_swu(Decimal("2.00"), "impact")
        assert "impact" in result.breakdown


# ── Quota limit constants ────────────────────────────────────────────


class TestQuotaLimitConstants:
    def test_wp_per_project_is_5(self) -> None:
        assert MAX_WORK_PACKAGES_PER_PROJECT == 5

    def test_tasks_per_wp_is_6(self) -> None:
        assert MAX_TASKS_PER_WORK_PACKAGE == 6

    def test_tasks_per_project_is_20(self) -> None:
        assert MAX_TASKS_PER_PROJECT == 20

    def test_ewu_per_task_is_8(self) -> None:
        assert MAX_EWU_PER_TASK == 8

    def test_active_projects_new_founder_is_2(self) -> None:
        assert MAX_ACTIVE_PROJECTS_NEW_FOUNDER == 2

    def test_open_seats_default_is_12(self) -> None:
        assert MAX_OPEN_SEATS_DEFAULT == 12

    def test_active_tasks_default_is_30(self) -> None:
        assert MAX_ACTIVE_TASKS_DEFAULT == 30

    def test_pending_apps_per_project_is_30(self) -> None:
        assert MAX_PENDING_APPLICATIONS_PER_PROJECT == 30

    def test_pending_apps_per_task_is_10(self) -> None:
        assert MAX_PENDING_APPLICATIONS_PER_TASK == 10

    def test_active_project_statuses_count(self) -> None:
        assert len(ACTIVE_PROJECT_STATUSES) == 4


# ── EWU cap gate verification ────────────────────────────────────────


class TestEwuCapGate:
    def test_collaboration_support_low_min_under_cap(self) -> None:
        """Lowest possible EWU: collaboration_support(0.6) x avg(1) x low(1.0) = 0.60."""
        inp = EwuInput(
            task_type="collaboration_support",
            risk_level="low",
            complexity=1,
            criticality=1,
            collaboration_complexity=1,
        )
        result = calculate_ewu(inp)
        assert result.ewu == Decimal("0.60")
        assert result.ewu <= MAX_EWU_PER_TASK

    def test_development_medium_mid_under_cap(self) -> None:
        """development(1.5) x avg(3) x medium(1.3) = 5.85."""
        inp = EwuInput(
            task_type="development",
            risk_level="medium",
            complexity=3,
            criticality=3,
            collaboration_complexity=3,
        )
        result = calculate_ewu(inp)
        assert result.ewu == Decimal("5.85")
        assert result.ewu <= MAX_EWU_PER_TASK

    def test_development_high_max_exceeds_cap(self) -> None:
        """development(1.5) x avg(5) x high(1.6) = 12.00, exceeds cap."""
        inp = EwuInput(
            task_type="development",
            risk_level="high",
            complexity=5,
            criticality=5,
            collaboration_complexity=5,
        )
        result = calculate_ewu(inp)
        assert result.ewu == Decimal("12.00")
        assert result.ewu > MAX_EWU_PER_TASK

    def test_documentation_high_max_under_cap(self) -> None:
        """documentation(0.7) x avg(5) x high(1.6) = 5.60, under cap."""
        inp = EwuInput(
            task_type="documentation",
            risk_level="high",
            complexity=5,
            criticality=5,
            collaboration_complexity=5,
        )
        result = calculate_ewu(inp)
        assert result.ewu == Decimal("5.60")
        assert result.ewu <= MAX_EWU_PER_TASK

    def test_ewu_input_rejects_complexity_zero(self) -> None:
        with pytest.raises(ValidationError):
            EwuInput(
                task_type="development",
                risk_level="low",
                complexity=0,
                criticality=1,
                collaboration_complexity=1,
            )

    def test_ewu_input_rejects_criticality_six(self) -> None:
        with pytest.raises(ValidationError):
            EwuInput(
                task_type="development",
                risk_level="low",
                complexity=1,
                criticality=6,
                collaboration_complexity=1,
            )

    def test_ewu_input_rejects_collab_negative(self) -> None:
        with pytest.raises(ValidationError):
            EwuInput(
                task_type="development",
                risk_level="low",
                complexity=1,
                criticality=1,
                collaboration_complexity=-1,
            )

    def test_ewu_quantized_to_two_decimal_places(self) -> None:
        """EWU result must be quantized to 0.01."""
        inp = EwuInput(
            task_type="research",
            risk_level="medium",
            complexity=2,
            criticality=3,
            collaboration_complexity=4,
        )
        result = calculate_ewu(inp)
        # Verify 2 decimal places
        assert result.ewu == result.ewu.quantize(Decimal("0.01"))

    def test_rwu_unknown_tier_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown reward tier"):
            calculate_rwu(Decimal("3.00"), "mythical")

    def test_swu_unknown_tier_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown sponsor tier"):
            calculate_swu(Decimal("3.00"), "mythical")
