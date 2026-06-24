# llm_judge

A production-grade **LLM-as-judge** evaluation pipeline, built on the Anthropic
SDK (Claude Opus 4.8 by default). It implements the LLM-as-judge family as a
small, composable library rather than a single technique:

- **Direct scoring** — one judge rates one response against weighted,
  rubric-backed criteria. Best for objective criteria (factual accuracy,
  instruction following, format compliance).
- **Pairwise comparison** — compares two responses with a two-pass
  position-swap protocol to mitigate position bias. Best for preference/quality
  judgments (tone, style, persuasiveness).
- **Rubric generation** — produces domain-specific rubrics (one level per score,
  observable characteristics, edge-case guidance) to cut evaluation variance.
- **Pipeline orchestrator** — loads criteria/rubrics, runs the primary scorer,
  applies bias mitigation, and calibrates confidence.
- **Agreement metrics** — Cohen's κ (incl. weighted), Spearman ρ, Kendall τ,
  precision/recall/F1, and a disagreement breakdown, for validating the judge
  against human labels. Pure-Python, no scipy/sklearn.

## Install

```bash
pip install -r ../requirements.txt   # anthropic, pydantic
```

Provide an Anthropic credential via the environment — `ANTHROPIC_API_KEY`,
`ANTHROPIC_AUTH_TOKEN`, or an `ant auth login` profile.

## Usage

### Direct scoring

```python
from llm_judge import EvaluationPipeline, Criterion

pipe = EvaluationPipeline(scale_min=1, scale_max=5)
criteria = [
    Criterion(name="Factual Accuracy",
              description="Are the claims correct?", weight=1.0),
    Criterion(name="Clarity",
              description="Easy for a beginner to follow?", weight=0.5),
]

result = pipe.score(prompt, response, criteria)
print(result.weighted_score)          # weight-normalized aggregate (computed in Python)
for ev in result.scores:
    print(ev.criterion, ev.score, ev.justification)
```

### Pairwise comparison (position-bias mitigated)

```python
result = pipe.compare(prompt, response_a, response_b, criteria)
print(result.winner.value, result.confidence)
print(result.position_consistency)    # consistent? + per-pass winners
```

Confidence is calibrated to position consistency: when the two swapped passes
agree, confidence is their average; when they disagree, the result is a `TIE`
with confidence `0.5` (the judge is position-biased on that pair).

### Generate and attach rubrics

```python
from llm_judge import Strictness

criteria = pipe.ensure_rubrics(
    criteria, domain="science education", strictness=Strictness.BALANCED
)
```

### Rank a small candidate set

```python
order = pipe.rank(prompt, [resp1, resp2, resp3], criteria)  # best-first indices
```

### Validate against human labels

```python
from llm_judge import cohen_kappa, spearman_rho, disagreement_breakdown

cohen_kappa(judge_scores, human_scores, weights="quadratic")
spearman_rho(judge_scores, human_scores)
disagreement_breakdown(judge_scores, human_scores)  # surfaces systematic skew
```

A runnable end-to-end demo is in [`../examples/run_evaluation.py`](../examples/run_evaluation.py),
and a reference-grounded one that judges summaries of the Titanic dataset is in
[`../examples/evaluate_titanic_summaries.py`](../examples/evaluate_titanic_summaries.py).

## Command line

The package ships a CLI (`python -m llm_judge`) that prints JSON to stdout, so it
composes with `jq` and pipes. Criteria are a JSON file: a list of
`{name, description, weight}` objects.

```bash
# Score one response
python -m llm_judge score --prompt-file q.txt --response-file a.txt -c criteria.json

# Compare two (two-pass, position-bias mitigated)
python -m llm_judge compare --prompt-file q.txt --a a.txt --b b.txt -c criteria.json

# Rank several (best first)
python -m llm_judge rank --prompt-file q.txt --responses r1.txt r2.txt -c criteria.json

# Generate a rubric for one criterion
python -m llm_judge rubric --name "Clarity" --description "Clear and readable?" --domain "support docs"
```

Global flags: `--model <id>` (default Claude Opus 4.8), `--scale-min`, `--scale-max`.

In **Cowork / Claude Code**, the same flows are exposed as the `/evaluate` skill
(`.claude/skills/evaluate/SKILL.md`), which drives this CLI.

## Design notes

- **Reasoning before score.** Response schemas list evidence/justification fields
  before the score/verdict. Since JSON is generated top-to-bottom, this enforces
  chain-of-thought-before-score, which improves reliability.
- **Structured outputs.** Every judge call is constrained to a Pydantic schema via
  `output_config.format`, so results come back validated — no brittle text parsing.
- **Aggregates computed in Python.** Weighted overall scores and pairwise
  aggregation are computed in code, not by the model, so they're deterministic
  and auditable.
- **Model is configurable per call.** Using a different model for evaluation than
  for generation is the recommended defense against self-enhancement bias.

## Layout

```
llm_judge/
  models.py          # Pydantic schemas: criteria, rubrics, results
  prompts.py         # Prompt builders for each approach
  client.py          # Anthropic SDK wrapper (model/effort/thinking + parsing)
  direct_scoring.py  # DirectScorer
  pairwise.py        # PairwiseComparator (two-pass position-swap)
  rubric.py          # RubricGenerator
  metrics.py         # Agreement metrics (pure Python)
  pipeline.py        # EvaluationPipeline orchestrator
  tests/             # Dependency-free unit tests (no API calls)
```

## Tests

```bash
python -m pytest llm_judge/tests -q
```

The tests cover the deterministic logic — metrics, weighted aggregation, the
position-swap mapping, and rubric rendering — and do not make API calls.
