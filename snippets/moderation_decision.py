"""
Pattern: an auditable, reversible moderation decision.

Illustrative rewrite from the Social Native moderation platform.

Two properties matter more than accuracy here:
  1. `flag` is always available, so the model can abstain instead of guessing.
  2. Every decision carries a rationale and its source, so a human reviewer
     can see *why* and send it back.
"""

from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    FLAG = "flag"  # abstention — routes to a human, never auto-resolves


class Source(str, Enum):
    BLOCKLIST = "blocklist"  # deterministic, runs before the model
    MODEL = "model"
    HUMAN = "human"  # always wins


@dataclass(frozen=True)
class ModerationResult:
    decision: Decision
    source: Source
    rationale: str
    confidence: float | None = None

    @property
    def needs_human(self) -> bool:
        return self.decision is Decision.FLAG or self.source is Source.MODEL


def resolve(
    blocklisted: bool,
    model_result: ModerationResult | None,
) -> ModerationResult:
    """Deterministic rules run first; the model never overrides them."""
    if blocklisted:
        return ModerationResult(
            decision=Decision.REJECT,
            source=Source.BLOCKLIST,
            rationale="Creator is on this brand's blocklist.",
        )

    if model_result is None:
        return ModerationResult(
            decision=Decision.FLAG,
            source=Source.MODEL,
            rationale="Classification unavailable — routed for human review.",
        )

    return model_result
