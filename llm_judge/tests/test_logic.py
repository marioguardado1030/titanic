"""Tests for pure aggregation/bias logic that doesn't require API calls."""

from llm_judge import Criterion, Rubric, RubricLevel, Verdict
from llm_judge.direct_scoring import DirectScorer
from llm_judge.models import CriterionEvaluation
from llm_judge.pairwise import _swap


def test_swap_maps_positions_back():
    assert _swap(Verdict.A) is Verdict.B
    assert _swap(Verdict.B) is Verdict.A
    assert _swap(Verdict.TIE) is Verdict.TIE


def test_weighted_score_respects_weights():
    criteria = [
        Criterion(name="acc", description="x", weight=1.0),
        Criterion(name="clarity", description="y", weight=0.5),
    ]
    evals = [
        CriterionEvaluation(criterion="acc", justification="j", score=5),
        CriterionEvaluation(criterion="clarity", justification="j", score=2),
    ]
    # (1.0*5 + 0.5*2) / 1.5 = 6/1.5 = 4.0
    assert DirectScorer._weighted_score(evals, criteria) == 4.0


def test_weighted_score_zero_weight_is_none():
    criteria = [Criterion(name="acc", description="x", weight=0.0)]
    evals = [CriterionEvaluation(criterion="acc", justification="j", score=5)]
    assert DirectScorer._weighted_score(evals, criteria) is None


def test_rubric_render_is_ordered_and_complete():
    rubric = Rubric(
        criterion_name="Readability",
        levels=[
            RubricLevel(score=3, label="Adequate", description="ok"),
            RubricLevel(score=1, label="Poor", description="bad",
                        characteristics=["no names"]),
        ],
    )
    text = rubric.render()
    # Levels render low-to-high regardless of input order.
    assert text.index("1 — Poor") < text.index("3 — Adequate")
    assert "no names" in text
