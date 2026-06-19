"""llm_judge — a production-grade LLM-as-judge evaluation pipeline.

Built on the Anthropic SDK (Claude Opus 4.8 by default), this package implements
the core LLM-as-judge family:

- Direct scoring of one response against weighted, rubric-backed criteria.
- Pairwise comparison with two-pass position-bias mitigation.
- Rubric generation for consistent, domain-specific scoring.
- A pipeline orchestrator that ties them together (load criteria -> score ->
  mitigate bias -> calibrate confidence).
- Agreement metrics for validating the judge against human labels.

Quick start
-----------
    from llm_judge import EvaluationPipeline, Criterion

    pipe = EvaluationPipeline()
    criteria = [Criterion(name="Factual Accuracy",
                          description="Are the claims correct?", weight=1.0)]
    result = pipe.score(prompt, response, criteria)
    print(result.weighted_score)
"""

from .client import JudgeClient, JudgeError
from .direct_scoring import DirectScorer
from .metrics import (
    accuracy,
    agreement_rate,
    cohen_kappa,
    disagreement_breakdown,
    kendall_tau,
    precision_recall_f1,
    spearman_rho,
)
from .models import (
    Criterion,
    CriterionComparison,
    CriterionEvaluation,
    DirectScoreResult,
    EdgeCase,
    PairwiseResponse,
    PairwiseResult,
    PositionConsistency,
    Rubric,
    RubricLevel,
    Strictness,
    Verdict,
)
from .pairwise import PairwiseComparator
from .pipeline import EvaluationPipeline
from .rubric import RubricGenerator

__version__ = "1.0.0"

__all__ = [
    # orchestration
    "EvaluationPipeline",
    "JudgeClient",
    "JudgeError",
    # evaluators
    "DirectScorer",
    "PairwiseComparator",
    "RubricGenerator",
    # models
    "Criterion",
    "CriterionEvaluation",
    "CriterionComparison",
    "DirectScoreResult",
    "PairwiseResponse",
    "PairwiseResult",
    "PositionConsistency",
    "Rubric",
    "RubricLevel",
    "EdgeCase",
    "Strictness",
    "Verdict",
    # metrics
    "agreement_rate",
    "accuracy",
    "cohen_kappa",
    "spearman_rho",
    "kendall_tau",
    "precision_recall_f1",
    "disagreement_breakdown",
]
