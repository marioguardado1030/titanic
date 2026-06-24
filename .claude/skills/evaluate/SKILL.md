---
name: evaluate
description: "Run LLM-as-judge evaluations with the repo's llm_judge package. USE WHEN the user wants to score an AI response against criteria, compare two responses to pick the better one, rank several candidates, or generate a scoring rubric — phrases like 'evaluate this answer', 'which response is better', 'rate this output', 'judge these', 'score against criteria', 'compare these two replies'. Drives the python -m llm_judge CLI. Requires code execution and an Anthropic credential."
---

# Evaluate (LLM-as-judge)

This skill runs the `llm_judge` package in this repo to evaluate AI-generated text:
direct scoring against weighted criteria, pairwise comparison with position-bias
mitigation, ranking, and rubric generation. Use it when the user wants a
structured, evidence-backed quality judgment rather than an off-the-cuff opinion.

## Prerequisites

- Run from the repo root.
- Dependencies: `pip install -r requirements.txt` (anthropic, pydantic).
- A credential in the environment: `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`,
  or an `ant auth login` profile. If none is set, tell the user — scoring calls
  the API and cannot run without it.

## Workflow

1. **Clarify the criteria.** Ask the user (or infer from context) what to judge
   on — e.g. factual accuracy, clarity, tone. Each criterion needs a name, a
   one-line description, and a weight. One criterion = one measurable aspect.

2. **Write a criteria file** (`criteria.json`) — a JSON list:

   ```json
   [{"name": "Factual Accuracy", "description": "Do the claims match the facts?", "weight": 1.0},
    {"name": "Clarity",          "description": "Clear and readable?",            "weight": 0.5}]
   ```

3. **Put the text in files** (`prompt.txt`, `response.txt`, etc.) or pass it
   inline with `--prompt` / `--response`.

4. **Run the matching command** (all print JSON to stdout):

   ```bash
   # Score one response
   python -m llm_judge score --prompt-file prompt.txt --response-file response.txt -c criteria.json

   # Compare two (two-pass, position-bias mitigated)
   python -m llm_judge compare --prompt-file prompt.txt --a a.txt --b b.txt -c criteria.json

   # Rank several (best first)
   python -m llm_judge rank --prompt-file prompt.txt --responses r1.txt r2.txt r3.txt -c criteria.json

   # Generate a rubric for one criterion
   python -m llm_judge rubric --name "Clarity" --description "Clear and readable?" --domain "support docs"
   ```

   Global flags: `--model <id>` (default Claude Opus 4.8), `--scale-min`,
   `--scale-max` (default 1–5).

5. **Summarize the JSON for the user** — report the scores/winner, the
   per-criterion justifications, and (for `compare`) whether the two position
   passes agreed. Surface low position-consistency as a caveat.

## Choosing the command

- Objective criteria with a clear bar (accuracy, instruction-following, format) →
  `score`.
- Subjective preference/quality (tone, style, persuasiveness) → `compare` / `rank`.
- For accuracy-style criteria, include the ground-truth facts in the prompt so the
  judge can check against them (see `examples/evaluate_titanic_summaries.py`).

## Cost note

`compare` runs two API passes per pair; `rank` is O(n²) comparisons. Keep
candidate sets small and warn the user before ranking many items.

## Python API

For programmatic use, import the package directly instead of the CLI — see
`llm_judge/README.md`. The CLI is a thin wrapper over `EvaluationPipeline`.
