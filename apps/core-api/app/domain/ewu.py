"""EWU (Effort Work Unit) calculation.

Based on .docs/ Schema Section 5.8 CalculateEwuInput:
- task_type, risk_level, complexity(1-5), criticality(1-5), collaboration_complexity(1-5)

Formula: EWU = base_weight * avg(complexity, criticality, collab) * risk_multiplier
"""

from decimal import Decimal

from pydantic import BaseModel, Field

# Base weights by task type
TASK_TYPE_WEIGHTS: dict[str, Decimal] = {
    "requirement_clarification": Decimal("0.8"),
    "research": Decimal("1.0"),
    "product_design": Decimal("1.2"),
    "development": Decimal("1.5"),
    "testing_fix": Decimal("1.0"),
    "documentation": Decimal("0.7"),
    "collaboration_support": Decimal("0.6"),
    "review_audit": Decimal("0.9"),
}

# Risk multipliers
RISK_MULTIPLIERS: dict[str, Decimal] = {
    "low": Decimal("1.0"),
    "medium": Decimal("1.3"),
    "high": Decimal("1.6"),
}


class EwuInput(BaseModel):
    """Input for EWU calculation."""

    task_type: str
    risk_level: str
    complexity: int = Field(ge=1, le=5)
    criticality: int = Field(ge=1, le=5)
    collaboration_complexity: int = Field(ge=1, le=5)


class EwuResult(BaseModel):
    """Result of EWU calculation."""

    ewu: Decimal
    breakdown: str


def calculate_ewu(params: EwuInput) -> EwuResult:
    """Calculate EWU based on task parameters."""
    if params.task_type not in TASK_TYPE_WEIGHTS:
        msg = f"Unknown task_type: '{params.task_type}'"
        raise ValueError(msg)
    if params.risk_level not in RISK_MULTIPLIERS:
        msg = f"Unknown risk_level: '{params.risk_level}'"
        raise ValueError(msg)
    base = TASK_TYPE_WEIGHTS[params.task_type]
    risk = RISK_MULTIPLIERS[params.risk_level]
    avg_complexity = Decimal(
        params.complexity + params.criticality + params.collaboration_complexity
    ) / Decimal("3")

    ewu = (base * avg_complexity * risk).quantize(Decimal("0.01"))

    breakdown = (
        f"base({params.task_type})={base} × "
        f"avg_complexity={avg_complexity:.2f} × "
        f"risk({params.risk_level})={risk} = {ewu}"
    )

    return EwuResult(ewu=ewu, breakdown=breakdown)
