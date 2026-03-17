"""Agent Card — formal capability description for platform agents.

Each agent (in-process or external) publishes an Agent Card describing
its capabilities, constraints, and interaction contract.
"""

from pydantic import BaseModel, Field


class AgentCapabilities(BaseModel):
    """What this agent can do."""

    delegation_types: list[str]
    input_schema: str = "TaskEnvelope + DelegationContract"
    output_schema: str = "AgentResult"
    supported_signal_sources: list[str] = Field(default_factory=list)


class AgentAuth(BaseModel):
    """Authentication requirements."""

    type: str = "bearer"
    required: bool = True


class AgentConstraints(BaseModel):
    """What this agent is NOT allowed to do."""

    forbidden_actions: list[str] = Field(
        default_factory=lambda: ["write_platform_state", "issue_vc"]
    )
    requires_human_review: bool = True
    max_timeout_seconds: int = 30


class AgentCard(BaseModel):
    """Formal capability description for a platform agent.

    Published at /.well-known/agent-card.json for external agents.
    Internal agents register their cards with the CoordinationService.
    """

    agent_id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    capabilities: AgentCapabilities
    auth: AgentAuth = Field(default_factory=AgentAuth)
    constraints: AgentConstraints = Field(default_factory=AgentConstraints)
    endpoint: str | None = None
    well_known_url: str | None = None
    protocol_version: str = "2.0"


# Registry of known agent cards (in-process agents)
AGENT_CARDS: dict[str, AgentCard] = {
    "matching_agent": AgentCard(
        agent_id="matching_agent",
        name="Matching Agent",
        description="Analyzes projects and applications to suggest matches",
        capabilities=AgentCapabilities(
            delegation_types=["matching"],
        ),
        constraints=AgentConstraints(
            requires_human_review=True,
            max_timeout_seconds=30,
        ),
    ),
    "review_prep_agent": AgentCard(
        agent_id="review_prep_agent",
        name="Review Prep Agent",
        description="Prepares evidence review brief for reviewers",
        capabilities=AgentCapabilities(
            delegation_types=["review_prep"],
        ),
        constraints=AgentConstraints(
            requires_human_review=True,
            max_timeout_seconds=30,
        ),
    ),
    "github_signal_agent": AgentCard(
        agent_id="github_signal_agent",
        name="GitHub Signal Agent",
        description="Normalizes GitHub data into platform signals",
        capabilities=AgentCapabilities(
            delegation_types=["github_signal"],
            supported_signal_sources=[
                "github_push",
                "github_pr",
                "github_review",
                "github_merge",
            ],
        ),
        constraints=AgentConstraints(
            requires_human_review=False,
            max_timeout_seconds=30,
        ),
    ),
    "vc_agent": AgentCard(
        agent_id="vc_agent",
        name="VC Agent",
        description="Checks issuance eligibility and produces recommendation",
        capabilities=AgentCapabilities(
            delegation_types=["vc_issuance"],
        ),
        constraints=AgentConstraints(
            requires_human_review=True,
            max_timeout_seconds=30,
            forbidden_actions=["write_platform_state", "issue_vc", "revoke_vc"],
        ),
    ),
}
