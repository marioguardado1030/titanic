"""Prompt builders for each evaluation approach.

Kept separate from the executors so prompt wording can be tuned and reviewed in
one place. Every prompt enforces the same core principles from the evaluation
literature: evidence before score, explicit bias instructions for pairwise, and
domain-specific rubric language where available.
"""

from __future__ import annotations

from .models import Criterion, Rubric, Strictness

DIRECT_SYSTEM = (
    "You are an expert evaluator assessing response quality. You are rigorous, "
    "evidence-driven, and calibrated. For every criterion you find specific "
    "evidence in the response first, then justify, then assign a score. You never "
    "reward length or verbosity for their own sake."
)

PAIRWISE_SYSTEM = (
    "You are an expert evaluator comparing two AI responses.\n\n"
    "## Critical instructions\n"
    "- Do NOT prefer a response because it is longer.\n"
    "- Do NOT prefer a response based on its position (first vs second).\n"
    "- Judge ONLY on quality against the specified criteria.\n"
    "- A tie is acceptable when responses are genuinely equivalent.\n"
    "- Analyze each response on its own merits before comparing."
)

RUBRIC_SYSTEM = (
    "You are an assessment-design expert. You write clear, domain-specific scoring "
    "rubrics with well-separated levels, observable characteristics, and explicit "
    "guidance for ambiguous edge cases."
)


def build_direct_prompt(
    prompt: str,
    response: str,
    criteria: list[Criterion],
    scale_min: int,
    scale_max: int,
) -> str:
    criteria_block = "\n".join(c.render(scale_max) for c in criteria)
    return f"""## Task
Evaluate the response below against each criterion.

## Original prompt
{prompt}

## Response to evaluate
{response}

## Criteria
{criteria_block}

## Instructions
For each criterion, in order:
1. Find specific evidence in the response (quote or describe concrete features).
2. Score on a {scale_min}-{scale_max} scale, following the rubric where provided.
3. Justify the score using the evidence you found.
4. Suggest one specific, actionable improvement.

Then write a short overall summary. Score only what the response actually does —
do not credit unstated intent, and do not penalize or reward length itself."""


def build_pairwise_prompt(
    prompt: str,
    response_a: str,
    response_b: str,
    criteria: list[Criterion],
) -> str:
    criteria_block = "\n".join(f"- {c.name}: {c.description}" for c in criteria)
    return f"""## Original prompt
{prompt}

## Response A
{response_a}

## Response B
{response_b}

## Comparison criteria
{criteria_block}

## Instructions
1. Analyze each response independently first.
2. Compare them on each criterion and pick a per-criterion winner (A, B, or tie).
3. Determine the overall winner (A, B, or tie) with a confidence from 0 to 1.

Remember: ignore length and position. Decide purely on quality against the criteria."""


def build_rubric_prompt(
    criterion_name: str,
    criterion_description: str,
    domain: str,
    scale_min: int,
    scale_max: int,
    strictness: Strictness,
) -> str:
    return f"""Generate a scoring rubric for the following criterion.

## Criterion
Name: {criterion_name}
Description: {criterion_description}
Domain: {domain}
Scale: {scale_min}-{scale_max}
Strictness: {strictness.value}

## Requirements
- Produce one level for EACH integer score from {scale_min} to {scale_max}.
- Each level needs a short label, a description, and 2-4 observable characteristics.
- Use vocabulary specific to the '{domain}' domain — not generic language.
- Calibrate boundaries to '{strictness.value}' strictness.
- Include 1-3 edge cases with explicit guidance for ambiguous situations.
- Include a few general scoring guidelines for consistent application."""
