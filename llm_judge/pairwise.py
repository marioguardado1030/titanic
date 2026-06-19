"""Pairwise comparison with position-bias mitigation.

Pairwise comparison is more reliable than direct scoring for preference/quality
judgments (tone, style, persuasiveness, creativity), but it is corrupted by
position bias — first-position responses are systematically favored. The fix,
applied here, is the two-pass swap protocol:

1. Pass 1: A in first position, B in second.
2. Pass 2: B in first position, A in second.
3. Map pass 2's verdict back to canonical A/B labels.
4. If the passes agree, that is the winner with averaged confidence.
   If they disagree, return TIE with confidence 0.5 (the model is position-biased
   on this pair, so no confident verdict is warranted).
"""

from __future__ import annotations

from typing import Optional

from .client import JudgeClient
from .models import (
    Criterion,
    PairwiseResponse,
    PairwiseResult,
    PositionConsistency,
    Verdict,
)
from .prompts import PAIRWISE_SYSTEM, build_pairwise_prompt


def _swap(verdict: Verdict) -> Verdict:
    """Translate a verdict from a swapped pass back to canonical A/B labels."""
    if verdict is Verdict.A:
        return Verdict.B
    if verdict is Verdict.B:
        return Verdict.A
    return Verdict.TIE


class PairwiseComparator:
    def __init__(self, client: Optional[JudgeClient] = None) -> None:
        self.client = client or JudgeClient()

    def compare(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        criteria: list[Criterion],
    ) -> PairwiseResult:
        if not criteria:
            raise ValueError("At least one criterion is required.")

        # Pass 1 — canonical ordering (A, B).
        first = self._one_pass(prompt, response_a, response_b, criteria)

        # Pass 2 — swapped ordering (B, A). The model's "A" now refers to the
        # canonical B, so we map its verdicts back before comparing.
        second_raw = self._one_pass(prompt, response_b, response_a, criteria)
        second_winner = _swap(second_raw.overall_winner)

        consistent = first.overall_winner == second_winner
        if consistent:
            winner = first.overall_winner
            confidence = round((first.confidence + second_raw.confidence) / 2, 4)
        else:
            # Disagreement across positions => position bias dominates this pair.
            winner = Verdict.TIE
            confidence = 0.5

        return PairwiseResult(
            winner=winner,
            confidence=confidence,
            position_consistency=PositionConsistency(
                consistent=consistent,
                first_pass_winner=first.overall_winner,
                second_pass_winner=second_winner,
            ),
            first_pass=first,
            second_pass=second_raw,
        )

    def _one_pass(
        self,
        prompt: str,
        first_response: str,
        second_response: str,
        criteria: list[Criterion],
    ) -> PairwiseResponse:
        user_prompt = build_pairwise_prompt(
            prompt, first_response, second_response, criteria
        )
        return self.client.parse(
            system=PAIRWISE_SYSTEM, prompt=user_prompt, schema=PairwiseResponse
        )
