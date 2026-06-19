"""Data models for the LLM-as-judge evaluation pipeline.

These Pydantic models serve two purposes:

1. They define the *structured output* schemas the judge model is constrained to
   (via ``output_config.format`` / ``messages.parse``), so every evaluation comes
   back as validated, machine-readable JSON rather than free text.
2. They are the public result types the pipeline returns to callers.

A deliberate design choice runs through the response schemas: evidence and
justification fields are declared *before* score/verdict fields. JSON is produced
top-to-bottom, so this forces the model to ground its reasoning before committing
to a number — the chain-of-thought-before-score pattern that the evaluation
literature finds improves reliability by 15-25%.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# --------------------------------------------------------------------------- #
# Criteria & rubrics (inputs)
# --------------------------------------------------------------------------- #


class Strictness(str, Enum):
    """How demanding a rubric's score boundaries are."""

    LENIENT = "lenient"
    BALANCED = "balanced"
    STRICT = "strict"


class RubricLevel(BaseModel):
    """One score level in a rubric (e.g. the '3 = Adequate' band)."""

    score: int = Field(description="The numeric score this level corresponds to.")
    label: str = Field(description="Short human label, e.g. 'Poor', 'Excellent'.")
    description: str = Field(description="What a response at this level looks like.")
    characteristics: list[str] = Field(
        default_factory=list,
        description="Observable features that define this level.",
    )


class EdgeCase(BaseModel):
    """Guidance for an ambiguous situation, to reduce evaluation variance."""

    situation: str = Field(description="The ambiguous situation.")
    guidance: str = Field(description="How the evaluator should handle it.")


class Rubric(BaseModel):
    """A full scoring rubric for a single criterion."""

    criterion_name: str
    scale_min: int = 1
    scale_max: int = 5
    strictness: Strictness = Strictness.BALANCED
    levels: list[RubricLevel] = Field(default_factory=list)
    edge_cases: list[EdgeCase] = Field(default_factory=list)
    scoring_guidelines: list[str] = Field(default_factory=list)

    def render(self) -> str:
        """Render the rubric as prompt-ready text."""
        lines = [
            f"Rubric for '{self.criterion_name}' "
            f"(scale {self.scale_min}-{self.scale_max}, {self.strictness.value}):"
        ]
        for level in sorted(self.levels, key=lambda lvl: lvl.score):
            lines.append(f"  {level.score} — {level.label}: {level.description}")
            for char in level.characteristics:
                lines.append(f"      • {char}")
        if self.edge_cases:
            lines.append("  Edge cases:")
            for ec in self.edge_cases:
                lines.append(f"      - {ec.situation} → {ec.guidance}")
        if self.scoring_guidelines:
            lines.append("  Scoring guidelines:")
            for g in self.scoring_guidelines:
                lines.append(f"      - {g}")
        return "\n".join(lines)


class Criterion(BaseModel):
    """A single, measurable aspect to evaluate.

    One criterion = one measurable aspect. Overloaded criteria (measuring several
    things at once) are unreliable, so keep these focused.
    """

    name: str
    description: str = Field(description="What this criterion measures.")
    weight: float = Field(
        default=1.0, ge=0.0, description="Relative importance (0-1 typical)."
    )
    rubric: Optional[Rubric] = None

    def render(self, scale_max: int) -> str:
        block = f"- {self.name} (weight {self.weight}): {self.description}"
        if self.rubric is not None:
            block += "\n" + _indent(self.rubric.render(), 2)
        return block


# --------------------------------------------------------------------------- #
# Direct scoring (outputs)
# --------------------------------------------------------------------------- #


class CriterionEvaluation(BaseModel):
    """The judge's evaluation of one criterion. Reasoning precedes the score."""

    criterion: str
    evidence: list[str] = Field(
        default_factory=list,
        description="Specific quotes/observations from the response.",
    )
    justification: str = Field(description="Why this score, grounded in the evidence.")
    score: int = Field(description="Score on the configured scale.")
    improvement: str = Field(
        default="", description="One specific, actionable improvement."
    )


class DirectScoreResult(BaseModel):
    """Result of direct scoring a single response against all criteria."""

    scores: list[CriterionEvaluation]
    summary: str = ""
    # Computed by the pipeline (not the model) for reliability:
    weighted_score: Optional[float] = None
    scale_min: int = 1
    scale_max: int = 5


# --------------------------------------------------------------------------- #
# Pairwise comparison (outputs)
# --------------------------------------------------------------------------- #


class Verdict(str, Enum):
    A = "A"
    B = "B"
    TIE = "tie"


class CriterionComparison(BaseModel):
    criterion: str
    reasoning: str = Field(description="Why one side wins this criterion.")
    winner: Verdict


class PairwiseResponse(BaseModel):
    """A single pass of pairwise comparison (one position ordering)."""

    per_criterion: list[CriterionComparison] = Field(default_factory=list)
    reasoning: str = Field(description="Overall reasoning for the verdict.")
    overall_winner: Verdict
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence 0-1.")


class PositionConsistency(BaseModel):
    consistent: bool
    first_pass_winner: Verdict
    second_pass_winner: Verdict


class PairwiseResult(BaseModel):
    """Position-bias-mitigated pairwise result aggregated over two passes."""

    winner: Verdict
    confidence: float
    position_consistency: PositionConsistency
    first_pass: PairwiseResponse
    second_pass: PairwiseResponse


def _indent(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line for line in text.splitlines())
