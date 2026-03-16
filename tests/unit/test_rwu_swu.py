"""Unit tests for RWU/SWU calculation logic."""

from decimal import Decimal

import pytest
from app.domain.rwu_swu import (
    DEFAULT_REWARD_TIER,
    DEFAULT_SPONSOR_TIER,
    REWARD_MULTIPLIERS,
    SPONSOR_MULTIPLIERS,
    calculate_rwu,
    calculate_swu,
)


class TestRewardMultipliers:
    def test_standard_tier(self):
        assert REWARD_MULTIPLIERS["standard"] == Decimal("1.2")

    def test_urgent_tier(self):
        assert REWARD_MULTIPLIERS["urgent"] == Decimal("1.5")

    def test_premium_tier(self):
        assert REWARD_MULTIPLIERS["premium"] == Decimal("2.0")

    def test_default_tier_is_standard(self):
        assert DEFAULT_REWARD_TIER == "standard"


class TestSponsorMultipliers:
    def test_standard_tier(self):
        assert SPONSOR_MULTIPLIERS["standard"] == Decimal("1.0")

    def test_matched_tier(self):
        assert SPONSOR_MULTIPLIERS["matched"] == Decimal("1.5")

    def test_impact_tier(self):
        assert SPONSOR_MULTIPLIERS["impact"] == Decimal("2.0")

    def test_default_tier_is_standard(self):
        assert DEFAULT_SPONSOR_TIER == "standard"


class TestCalculateRwu:
    def test_standard_default(self):
        result = calculate_rwu(Decimal("4.50"))
        assert result.rwu == Decimal("5.40")  # 4.50 × 1.2

    def test_urgent_tier(self):
        result = calculate_rwu(Decimal("4.50"), "urgent")
        assert result.rwu == Decimal("6.75")  # 4.50 × 1.5

    def test_premium_tier(self):
        result = calculate_rwu(Decimal("4.50"), "premium")
        assert result.rwu == Decimal("9.00")  # 4.50 × 2.0

    def test_zero_ewu(self):
        result = calculate_rwu(Decimal("0.00"))
        assert result.rwu == Decimal("0.00")

    def test_small_ewu(self):
        result = calculate_rwu(Decimal("0.50"))
        assert result.rwu == Decimal("0.60")  # 0.50 × 1.2

    def test_max_ewu(self):
        result = calculate_rwu(Decimal("8.00"))
        assert result.rwu == Decimal("9.60")  # 8.00 × 1.2

    def test_unknown_tier_raises(self):
        with pytest.raises(ValueError, match="Unknown reward tier"):
            calculate_rwu(Decimal("4.50"), "unknown")

    def test_breakdown_format(self):
        result = calculate_rwu(Decimal("4.50"), "standard")
        assert "EWU=4.50" in result.breakdown
        assert "reward(standard)=1.2" in result.breakdown


class TestCalculateSwu:
    def test_standard_default(self):
        result = calculate_swu(Decimal("4.50"))
        assert result.swu == Decimal("4.50")  # 4.50 × 1.0

    def test_matched_tier(self):
        result = calculate_swu(Decimal("4.50"), "matched")
        assert result.swu == Decimal("6.75")  # 4.50 × 1.5

    def test_impact_tier(self):
        result = calculate_swu(Decimal("4.50"), "impact")
        assert result.swu == Decimal("9.00")  # 4.50 × 2.0

    def test_zero_ewu(self):
        result = calculate_swu(Decimal("0.00"))
        assert result.swu == Decimal("0.00")

    def test_unknown_tier_raises(self):
        with pytest.raises(ValueError, match="Unknown sponsor tier"):
            calculate_swu(Decimal("4.50"), "invalid")

    def test_breakdown_format(self):
        result = calculate_swu(Decimal("4.50"), "matched")
        assert "EWU=4.50" in result.breakdown
        assert "sponsor(matched)=1.5" in result.breakdown
