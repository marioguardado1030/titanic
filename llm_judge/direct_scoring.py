"""Direct scoring: one judge rates one response against weighted criteria.

Best for objective criteria with a clear bar — factual accuracy, instruction
following, format compliance. The judge produces evidence and a justification
before each score; the weighted overall is computed here in Python (not by the
model) so the aggregate is deterministic and auditable.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from .client import JudgeClient
from .models import Criterion, CriterionEvaluation, DirectScoreResult
from .prompts import DIRECT_SYSTEM, build_direct_prompt


class _DirectResponse(BaseModel):
    """Schema the model is constrained to (overall aggregate added afterwards)."""

    scores: list[CriterionEvaluation]
    summary: str = ""


class DirectScorer:
    def __init__(self, client: Optional[JudgeClient] = None) -> None:
        self.client = client or JudgeClient()

    def score(
        self,
        prompt: str,
        response: str,
        criteria: list[Criterion],
        *,
        scale_min: int = 1,
        scale_max: int = 5,
    ) -> DirectScoreResult:
        if not criteria:
            raise ValueError("At least one criterion is required.")

        user_prompt = build_direct_prompt(
            prompt, response, criteria, scale_min, scale_max
        )
        raw = self.client.parse(
            system=DIRECT_SYSTEM, prompt=user_prompt, schema=_DirectResponse
        )

        weighted = self._weighted_score(raw.scores, criteria)
        return DirectScoreResult(
            scores=raw.scores,
            summary=raw.summary,
            weighted_score=weighted,
            scale_min=scale_min,
            scale_max=scale_max,
        )

    @staticmethod
    def _weighted_score(
        evaluations: list[CriterionEvaluation], criteria: list[Criterion]
    ) -> Optional[float]:
        """Weighted mean of per-criterion scores, normalized by total weight."""
        weights = {c.name: c.weight for c in criteria}
        total_weight = 0.0
        acc = 0.0
        for ev in evaluations:
            w = weights.get(ev.criterion, 1.0)
            acc += w * ev.score
            total_weight += w
        if total_weight == 0:
            return None
        return round(acc / total_weight, 4)
