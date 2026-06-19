"""End-to-end demo of the llm_judge pipeline.

Requires a working Anthropic credential in the environment (ANTHROPIC_API_KEY,
ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile). Run from the repo root:

    python -m examples.run_evaluation
"""

from llm_judge import Criterion, EvaluationPipeline, Strictness

PROMPT = "What causes the seasons on Earth?"

GOOD = (
    "Seasons are caused by Earth's tilted axis (about 23.5°). As Earth orbits the "
    "Sun, each hemisphere is tilted toward the Sun for part of the year — receiving "
    "more direct sunlight and longer days — and away from it for another part."
)

WEAK = (
    "Seasons happen because the Earth gets closer to and farther from the Sun as "
    "it orbits, so it's hotter in summer and colder in winter."
)


def main() -> None:
    pipe = EvaluationPipeline(scale_min=1, scale_max=5)

    criteria = [
        Criterion(
            name="Factual Accuracy",
            description="Are the scientific claims correct?",
            weight=1.0,
        ),
        Criterion(
            name="Clarity",
            description="Is the explanation easy for a beginner to follow?",
            weight=0.5,
        ),
    ]

    # Attach generated, domain-specific rubrics to any criterion without one.
    criteria = pipe.ensure_rubrics(
        criteria, domain="science education", strictness=Strictness.BALANCED
    )

    # --- Direct scoring (objective criteria) ------------------------------- #
    print("=== Direct scoring: GOOD response ===")
    result = pipe.score(PROMPT, GOOD, criteria)
    for ev in result.scores:
        print(f"  {ev.criterion}: {ev.score}  — {ev.justification}")
    print(f"  weighted score: {result.weighted_score}")

    # --- Pairwise comparison (preference; position-bias mitigated) --------- #
    print("\n=== Pairwise: GOOD vs WEAK ===")
    comparison = pipe.compare(PROMPT, GOOD, WEAK, criteria)
    print(f"  winner: {comparison.winner.value}  confidence: {comparison.confidence}")
    pc = comparison.position_consistency
    print(
        f"  position-consistent: {pc.consistent} "
        f"(pass1={pc.first_pass_winner.value}, pass2={pc.second_pass_winner.value})"
    )


if __name__ == "__main__":
    main()
