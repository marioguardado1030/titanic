"""Reference-grounded evaluation against the Titanic dataset.

This is a realistic use of the pipeline: judging AI-written summaries of a
dataset. Because "factual accuracy" needs a ground truth, the script computes
real statistics from titanic_clean.csv and injects them into the prompt as a
reference, then scores two candidate summaries — one accurate, one with a
planted error — and compares them.

Run from the repo root (needs an Anthropic credential):

    python -m examples.evaluate_titanic_summaries
"""

from __future__ import annotations

import csv
import os
from collections import Counter

from llm_judge import Criterion, EvaluationPipeline

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "titanic_clean.csv")


def dataset_facts() -> dict:
    """Compute a few ground-truth facts from the cleaned Titanic CSV."""
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows.append(row)

    n = len(rows)
    survived = sum(1 for r in rows if r["survived"] == "1")
    by_class = Counter(r["pclass"] for r in rows)
    sex = Counter(r["sex"] for r in rows)
    return {
        "n_passengers": n,
        "survival_rate_pct": round(100 * survived / n, 1),
        "passengers_by_class": dict(by_class),
        "passengers_by_sex": dict(sex),
    }


def reference_block(facts: dict) -> str:
    return (
        "Reference facts (ground truth, computed from the dataset):\n"
        f"- Passengers: {facts['n_passengers']}\n"
        f"- Overall survival rate: {facts['survival_rate_pct']}%\n"
        f"- By class: {facts['passengers_by_class']}\n"
        f"- By sex: {facts['passengers_by_sex']}\n"
    )


def main() -> None:
    facts = dataset_facts()
    print("Computed facts:", facts, "\n")

    prompt = (
        "Summarize the Titanic passenger dataset for a general audience.\n\n"
        + reference_block(facts)
    )

    accurate = (
        f"The dataset covers {facts['n_passengers']} passengers. About "
        f"{facts['survival_rate_pct']}% survived. Passengers spanned three ticket "
        "classes, and the group included both men and women, with men in the majority."
    )

    flawed = (
        "The dataset covers about 900 passengers, and the large majority — over "
        "70% — survived the disaster. Nearly everyone travelled first class."
    )  # planted errors: wrong count, wrong survival rate, wrong class distribution

    criteria = [
        Criterion(name="Factual Accuracy",
                  description="Do the claims match the reference facts?", weight=1.0),
        Criterion(name="Clarity",
                  description="Is it clear and readable for a general audience?",
                  weight=0.5),
    ]

    pipe = EvaluationPipeline(scale_min=1, scale_max=5)

    print("=== Direct scoring ===")
    for label, summary in (("accurate", accurate), ("flawed", flawed)):
        result = pipe.score(prompt, summary, criteria)
        print(f"\n[{label}] weighted score: {result.weighted_score}")
        for ev in result.scores:
            print(f"  {ev.criterion}: {ev.score} — {ev.justification}")

    print("\n=== Pairwise (accurate vs flawed) ===")
    cmp = pipe.compare(prompt, accurate, flawed, criteria)
    print(f"winner: {cmp.winner.value}  confidence: {cmp.confidence}  "
          f"position-consistent: {cmp.position_consistency.consistent}")


if __name__ == "__main__":
    main()
