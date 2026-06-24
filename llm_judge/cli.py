"""Command-line interface for the llm_judge pipeline.

Usage:
    python -m llm_judge score    --prompt-file q.txt --response-file a.txt --criteria c.json
    python -m llm_judge compare  --prompt "..." --a a.txt --b b.txt --criteria c.json
    python -m llm_judge rank      --prompt-file q.txt --responses r1.txt r2.txt r3.txt -c c.json
    python -m llm_judge rubric   --name "Clarity" --description "..." --domain "support"

A criteria file is JSON: a list of objects with name/description/weight, e.g.

    [{"name": "Factual Accuracy", "description": "Are the claims correct?", "weight": 1.0},
     {"name": "Clarity",         "description": "Easy to follow?",         "weight": 0.5}]

Results are printed as JSON to stdout, so the command composes with jq and pipes.
The scoring commands call the Anthropic API and need a credential in the
environment (ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN / an `ant auth login` profile).
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from .models import Criterion, Strictness


def _read(text: Optional[str], path: Optional[str], *, label: str) -> str:
    """Resolve a value given either inline text or a file path (exactly one)."""
    if text is not None and path is not None:
        raise SystemExit(f"Provide only one of --{label} / --{label}-file.")
    if text is not None:
        return text
    if path is not None:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    raise SystemExit(f"Provide --{label} or --{label}-file.")


def load_criteria(path: str) -> list[Criterion]:
    """Load a criteria list from a JSON file into validated Criterion objects."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise SystemExit("Criteria file must contain a JSON list of objects.")
    try:
        return [Criterion(**item) for item in data]
    except TypeError as exc:  # non-dict entries
        raise SystemExit(f"Invalid criteria file: {exc}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llm_judge", description="LLM-as-judge evaluation CLI."
    )
    parser.add_argument("--model", help="Override the judge model.")
    parser.add_argument("--scale-min", type=int, default=1)
    parser.add_argument("--scale-max", type=int, default=5)
    sub = parser.add_subparsers(dest="command", required=True)

    def add_criteria(p: argparse.ArgumentParser) -> None:
        p.add_argument("-c", "--criteria", required=True, help="Path to criteria JSON.")

    def add_prompt(p: argparse.ArgumentParser) -> None:
        p.add_argument("--prompt", help="Inline prompt text.")
        p.add_argument("--prompt-file", help="File with the prompt text.")

    s = sub.add_parser("score", help="Direct-score one response.")
    add_prompt(s)
    s.add_argument("--response", help="Inline response text.")
    s.add_argument("--response-file", help="File with the response text.")
    add_criteria(s)

    c = sub.add_parser("compare", help="Pairwise-compare two responses.")
    add_prompt(c)
    c.add_argument("--a", required=True, help="File with response A.")
    c.add_argument("--b", required=True, help="File with response B.")
    add_criteria(c)

    r = sub.add_parser("rank", help="Rank several responses (best first).")
    add_prompt(r)
    r.add_argument("--responses", nargs="+", required=True, help="Response files.")
    add_criteria(r)

    rb = sub.add_parser("rubric", help="Generate a rubric for one criterion.")
    rb.add_argument("--name", required=True)
    rb.add_argument("--description", required=True)
    rb.add_argument("--domain", default="general")
    rb.add_argument(
        "--strictness",
        choices=[s.value for s in Strictness],
        default=Strictness.BALANCED.value,
    )

    return parser


def _emit(model) -> None:
    print(model.model_dump_json(indent=2))


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    # Imported lazily so `--help` and arg parsing don't require the SDK/credentials.
    from .client import JudgeClient
    from .pipeline import EvaluationPipeline

    client = JudgeClient(model=args.model) if args.model else JudgeClient()
    pipe = EvaluationPipeline(
        client, scale_min=args.scale_min, scale_max=args.scale_max
    )

    if args.command == "score":
        prompt = _read(args.prompt, args.prompt_file, label="prompt")
        response = _read(args.response, args.response_file, label="response")
        _emit(pipe.score(prompt, response, load_criteria(args.criteria)))

    elif args.command == "compare":
        prompt = _read(args.prompt, args.prompt_file, label="prompt")
        with open(args.a, encoding="utf-8") as fh:
            resp_a = fh.read()
        with open(args.b, encoding="utf-8") as fh:
            resp_b = fh.read()
        _emit(pipe.compare(prompt, resp_a, resp_b, load_criteria(args.criteria)))

    elif args.command == "rank":
        prompt = _read(args.prompt, args.prompt_file, label="prompt")
        responses = []
        for path in args.responses:
            with open(path, encoding="utf-8") as fh:
                responses.append(fh.read())
        order = pipe.rank(prompt, responses, load_criteria(args.criteria))
        print(json.dumps({"order": order,
                          "ranked_files": [args.responses[i] for i in order]}, indent=2))

    elif args.command == "rubric":
        rubric = pipe.rubrics.generate(
            args.name,
            args.description,
            domain=args.domain,
            scale_min=args.scale_min,
            scale_max=args.scale_max,
            strictness=Strictness(args.strictness),
        )
        _emit(rubric)

    return 0


if __name__ == "__main__":
    sys.exit(main())
