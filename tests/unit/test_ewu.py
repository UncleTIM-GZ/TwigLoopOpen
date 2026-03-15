"""Tests for app.domain.ewu — EWU calculation logic."""

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


# ── Constants ─────────────────────────────────────────────────────


class TestEwuConstants:
    def test_task_type_weights_non_empty(self) -> None:
        assert len(TASK_TYPE_WEIGHTS) > 0

    def test_task_type_weights_all_positive(self) -> None:
        for k, v in TASK_TYPE_WEIGHTS.items():
            assert v > 0, f"Weight for '{k}' should be positive"

    def test_development_has_highest_weight(self) -> None:
        assert TASK_TYPE_WEIGHTS["development"] >= max(
            v for k, v in TASK_TYPE_WEIGHTS.items() if k != "development"
        )

    def test_risk_multipliers_low_is_one(self) -> None:
        assert RISK_MULTIPLIERS["low"] == Decimal("1.0")

    def test_risk_multipliers_increasing(self) -> None:
        assert RISK_MULTIPLIERS["low"] < RISK_MULTIPLIERS["medium"] < RISK_MULTIPLIERS["high"]


# ── Basic calculation ─────────────────────────────────────────────


class TestCalculateEwu:
    def test_basic_development_low_risk(self) -> None:
        inp = EwuInput(
            task_type="development",
            risk_level="low",
            complexity=3,
            criticality=3,
            collaboration_complexity=3,
        )
        result = calculate_ewu(inp)
        # base=1.5, avg=3.0, risk=1.0 => 1.5 * 3.0 * 1.0 = 4.50
        assert result.ewu == Decimal("4.50")

    def test_documentation_low_risk_min_values(self) -> None:
        inp = EwuInput(
            task_type="documentation",
            risk_level="low",
            complexity=1,
            criticality=1,
            collaboration_complexity=1,
        )
        result = calculate_ewu(inp)
        # base=0.7, avg=1.0, risk=1.0 => 0.70
        assert result.ewu == Decimal("0.70")

    def test_research_high_risk_max_values(self) -> None:
        inp = EwuInput(
            task_type="research",
            risk_level="high",
            complexity=5,
            criticality=5,
            collaboration_complexity=5,
        )
        result = calculate_ewu(inp)
        # base=1.0, avg=5.0, risk=1.6 => 8.00
        assert result.ewu == Decimal("8.00")


# ── Different task types produce different weights ────────────────


class TestTaskTypeVariation:
    def test_development_vs_documentation(self) -> None:
        """Development should produce higher EWU than documentation with same params."""
        params = {"risk_level": "low", "complexity": 3, "criticality": 3, "collaboration_complexity": 3}
        dev = calculate_ewu(EwuInput(task_type="development", **params))
        doc = calculate_ewu(EwuInput(task_type="documentation", **params))
        assert dev.ewu > doc.ewu

    def test_all_task_types_produce_valid_result(self) -> None:
        for task_type in TASK_TYPE_WEIGHTS:
            inp = EwuInput(
                task_type=task_type,
                risk_level="low",
                complexity=3,
                criticality=3,
                collaboration_complexity=3,
            )
            result = calculate_ewu(inp)
            assert result.ewu > 0


# ── Risk multipliers ─────────────────────────────────────────────


class TestRiskMultipliers:
    def test_medium_risk_higher_than_low(self) -> None:
        params = {"task_type": "development", "complexity": 3, "criticality": 3, "collaboration_complexity": 3}
        low = calculate_ewu(EwuInput(risk_level="low", **params))
        med = calculate_ewu(EwuInput(risk_level="medium", **params))
        assert med.ewu > low.ewu

    def test_high_risk_higher_than_medium(self) -> None:
        params = {"task_type": "development", "complexity": 3, "criticality": 3, "collaboration_complexity": 3}
        med = calculate_ewu(EwuInput(risk_level="medium", **params))
        high = calculate_ewu(EwuInput(risk_level="high", **params))
        assert high.ewu > med.ewu

    def test_risk_multiplier_exact_values(self) -> None:
        base_params = {"task_type": "research", "complexity": 2, "criticality": 2, "collaboration_complexity": 2}
        low = calculate_ewu(EwuInput(risk_level="low", **base_params))
        med = calculate_ewu(EwuInput(risk_level="medium", **base_params))
        high = calculate_ewu(EwuInput(risk_level="high", **base_params))
        # base=1.0, avg=2.0 => low=2.00, med=2.60, high=3.20
        assert low.ewu == Decimal("2.00")
        assert med.ewu == Decimal("2.60")
        assert high.ewu == Decimal("3.20")


# ── Edge cases ────────────────────────────────────────────────────


class TestEdgeCases:
    def test_unknown_task_type_raises_value_error(self) -> None:
        inp = EwuInput(
            task_type="unknown_type",
            risk_level="low",
            complexity=1,
            criticality=1,
            collaboration_complexity=1,
        )
        with pytest.raises(ValueError, match="Unknown task_type"):
            calculate_ewu(inp)

    def test_unknown_risk_level_raises_value_error(self) -> None:
        inp = EwuInput(
            task_type="development",
            risk_level="extreme",
            complexity=1,
            criticality=1,
            collaboration_complexity=1,
        )
        with pytest.raises(ValueError, match="Unknown risk_level"):
            calculate_ewu(inp)

    def test_complexity_below_range_rejected_by_pydantic(self) -> None:
        with pytest.raises(ValidationError):
            EwuInput(
                task_type="development",
                risk_level="low",
                complexity=0,
                criticality=1,
                collaboration_complexity=1,
            )

    def test_complexity_above_range_rejected_by_pydantic(self) -> None:
        with pytest.raises(ValidationError):
            EwuInput(
                task_type="development",
                risk_level="low",
                complexity=6,
                criticality=1,
                collaboration_complexity=1,
            )

    def test_result_has_breakdown_string(self) -> None:
        inp = EwuInput(
            task_type="development",
            risk_level="low",
            complexity=3,
            criticality=3,
            collaboration_complexity=3,
        )
        result = calculate_ewu(inp)
        assert isinstance(result.breakdown, str)
        assert "development" in result.breakdown
        assert "low" in result.breakdown

    def test_result_is_ewu_result_type(self) -> None:
        inp = EwuInput(
            task_type="development",
            risk_level="low",
            complexity=1,
            criticality=1,
            collaboration_complexity=1,
        )
        result = calculate_ewu(inp)
        assert isinstance(result, EwuResult)

    def test_asymmetric_complexity_values(self) -> None:
        """When complexity dimensions differ, average is used."""
        inp = EwuInput(
            task_type="research",
            risk_level="low",
            complexity=1,
            criticality=5,
            collaboration_complexity=3,
        )
        result = calculate_ewu(inp)
        # base=1.0, avg=(1+5+3)/3=3.0, risk=1.0 => 3.00
        assert result.ewu == Decimal("3.00")
