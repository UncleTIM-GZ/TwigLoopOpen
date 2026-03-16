"""RWU / SWU (Reward / Sponsor Work Unit) calculation.

v1: deterministic, explainable, testable.
v1 frozen: tier 参数保留但暂不对外开放，所有调用使用 default tier。
- RWU = EWU × reward_multiplier  (recruitment projects)
- SWU = EWU × sponsor_multiplier (sponsored public-benefit projects)
"""

from decimal import Decimal

from pydantic import BaseModel

# Reward multipliers for recruitment projects
REWARD_MULTIPLIERS: dict[str, Decimal] = {
    "standard": Decimal("1.2"),
    "urgent": Decimal("1.5"),
    "premium": Decimal("2.0"),
}

# Sponsor multipliers for public-benefit projects
SPONSOR_MULTIPLIERS: dict[str, Decimal] = {
    "standard": Decimal("1.0"),
    "matched": Decimal("1.5"),
    "impact": Decimal("2.0"),
}

DEFAULT_REWARD_TIER = "standard"
DEFAULT_SPONSOR_TIER = "standard"


class RwuResult(BaseModel):
    rwu: Decimal
    breakdown: str


class SwuResult(BaseModel):
    swu: Decimal
    breakdown: str


def calculate_rwu(ewu: Decimal, tier: str = DEFAULT_REWARD_TIER) -> RwuResult:
    """Calculate RWU from EWU and reward tier.

    v1: 固定使用 standard tier (1.2x)。Tier 参数保留用于后续升级。
    """
    if tier not in REWARD_MULTIPLIERS:
        msg = f"Unknown reward tier: '{tier}'"
        raise ValueError(msg)
    multiplier = REWARD_MULTIPLIERS[tier]
    rwu = (ewu * multiplier).quantize(Decimal("0.01"))
    breakdown = f"EWU={ewu} × reward({tier})={multiplier} = {rwu}"
    return RwuResult(rwu=rwu, breakdown=breakdown)


def calculate_swu(ewu: Decimal, tier: str = DEFAULT_SPONSOR_TIER) -> SwuResult:
    """Calculate SWU from EWU and sponsor tier.

    v1: fixed standard tier (1.0x = equals EWU).
    Design intent: SWU equals EWU in v1; differentiated multiplier deferred to v2.
    """
    if tier not in SPONSOR_MULTIPLIERS:
        msg = f"Unknown sponsor tier: '{tier}'"
        raise ValueError(msg)
    multiplier = SPONSOR_MULTIPLIERS[tier]
    swu = (ewu * multiplier).quantize(Decimal("0.01"))
    breakdown = f"EWU={ewu} × sponsor({tier})={multiplier} = {swu}"
    return SwuResult(swu=swu, breakdown=breakdown)
