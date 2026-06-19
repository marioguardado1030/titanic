"""The evaluation pipeline: the layered orchestrator from the skill diagram.

    Input: response + prompt + criteria
        -> Criteria loader (rubrics, weights)
        -> Primary scorer (direct or pairwise)
        -> Bias mitigation (position swap for pairwise)
        -> Confidence scoring (calibrated to position consistency)
    Output: scores + justifications + confidence

It exposes one object that decides between direct scoring and pairwise comparison,
and that can auto-generate rubrics for criteria that lack them.

Decision rule (matches the skill's decision tree):
  - objective ground truth ............ direct scoring
  - preference / quality judgment ..... pairwise comparison
"""

from __future__ import annotations

from typing import Optional

from .client import JudgeClient
from .direct_scoring import DirectScorer
from .models import Criterion, DirectScoreResult, PairwiseResult, Strictness
from .pairwise import PairwiseComparator
from .rubric import RubricGenerator


class EvaluationPipeline:
    """One entry point for direct scoring, pairwise comparison, and rubric prep."""

    def __init__(
        self,
        client: Optional[JudgeClient] = None,
        *,
        scale_min: int = 1,
        scale_max: int = 5,
    ) -> None:
        self.client = client or JudgeClient()
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.direct = DirectScorer(self.client)
        self.pairwise = PairwiseComparator(self.client)
        self.rubrics = RubricGenerator(self.client)

    # -- criteria loader ---------------------------------------------------- #

    def ensure_rubrics(
        self,
        criteria: list[Criterion],
        *,
        domain: str = "general",
        strictness: Strictness = Strictness.BALANCED,
    ) -> list[Criterion]:
        """Generate and attach a rubric to any criterion that lacks one.

        Returns new ``Criterion`` instances; the inputs are not mutated.
        """
        prepared: list[Criterion] = []
        for c in criteria:
            if c.rubric is not None:
                prepared.append(c)
                continue
            rubric = self.rubrics.generate(
                c.name,
                c.description,
                domain=domain,
                scale_min=self.scale_min,
                scale_max=self.scale_max,
                strictness=strictness,
            )
            prepared.append(c.model_copy(update={"rubric": rubric}))
        return prepared

    # -- primary scorers ---------------------------------------------------- #

    def score(
        self,
        prompt: str,
        response: str,
        criteria: list[Criterion],
    ) -> DirectScoreResult:
        """Direct scoring — use for objective criteria with a clear bar."""
        return self.direct.score(
            prompt,
            response,
            criteria,
            scale_min=self.scale_min,
            scale_max=self.scale_max,
        )

    def compare(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        criteria: list[Criterion],
    ) -> PairwiseResult:
        """Pairwise comparison with position-bias mitigation — use for preferences."""
        return self.pairwise.compare(prompt, response_a, response_b, criteria)

    def rank(
        self,
        prompt: str,
        responses: list[str],
        criteria: list[Criterion],
    ) -> list[int]:
        """Rank responses by round-robin pairwise wins (bias-mitigated each pair).

        Returns indices into ``responses``, best first. Ties in win-count are
        broken by total confidence accrued. Cost is O(n^2) comparisons, each of
        which runs two position-swapped passes — use for small candidate sets.
        """
        n = len(responses)
        if n < 2:
            return list(range(n))

        wins = [0.0] * n
        confidence = [0.0] * n
        for i in range(n):
            for j in range(i + 1, n):
                result = self.compare(prompt, responses[i], responses[j], criteria)
                if result.winner.value == "A":
                    wins[i] += 1
                    confidence[i] += result.confidence
                elif result.winner.value == "B":
                    wins[j] += 1
                    confidence[j] += result.confidence
                else:  # tie
                    wins[i] += 0.5
                    wins[j] += 0.5

        return sorted(range(n), key=lambda k: (wins[k], confidence[k]), reverse=True)
