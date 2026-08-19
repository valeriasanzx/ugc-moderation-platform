"""
Pattern: build a moderation prompt from per-brand structured guidelines.

Illustrative rewrite from the Social Native moderation platform.
Contains no company code, production prompts, or client data.

The point: onboarding a brand is filling in this dataclass, not editing
a prompt string in the codebase. Brands own their own rules.
"""

from dataclasses import dataclass, field


@dataclass
class BrandGuidelines:
    """Supplied by the client through a form — not authored by engineering."""

    brand: str
    prohibited: list[str] = field(default_factory=list)
    required: list[str] = field(default_factory=list)
    tone: str | None = None
    notes: str | None = None


def build_classification_prompt(g: BrandGuidelines) -> str:
    """Render brand rules into the instruction block for the classifier."""
    sections = [
        f"You are moderating user-generated content for {g.brand}.",
        "Decide one of: approve, reject, flag.",
        "",
        "Return `flag` whenever you are uncertain, or when the content is "
        "borderline against a rule below. A flagged item goes to a human "
        "reviewer, which is the correct and inexpensive outcome. Do not guess.",
        "",
        "Always give a one-sentence rationale citing the specific rule you "
        "applied, so a reviewer can disagree with you.",
    ]

    if g.prohibited:
        sections += ["", "Reject content that contains any of the following:"]
        sections += [f"  - {rule}" for rule in g.prohibited]

    if g.required:
        sections += ["", "Content must satisfy all of the following to be approved:"]
        sections += [f"  - {rule}" for rule in g.required]

    if g.tone:
        sections += ["", f"Brand tone: {g.tone}"]

    if g.notes:
        sections += ["", f"Additional brand notes: {g.notes}"]

    return "\n".join(sections)
