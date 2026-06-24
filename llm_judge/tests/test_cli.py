"""Tests for CLI parsing/loading that don't require API calls."""

import json

import pytest

from llm_judge import cli


def test_parser_score_args():
    args = cli.build_parser().parse_args(
        ["score", "--prompt", "q", "--response", "a", "-c", "c.json"]
    )
    assert args.command == "score"
    assert args.prompt == "q"
    assert args.scale_max == 5  # default


def test_parser_requires_subcommand():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args([])


def test_load_criteria_roundtrip(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps([
        {"name": "Accuracy", "description": "correct?", "weight": 1.0},
        {"name": "Clarity", "description": "clear?", "weight": 0.5},
    ]))
    criteria = cli.load_criteria(str(path))
    assert [c.name for c in criteria] == ["Accuracy", "Clarity"]
    assert criteria[1].weight == 0.5


def test_load_criteria_rejects_non_list(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"name": "x"}))
    with pytest.raises(SystemExit):
        cli.load_criteria(str(path))


def test_read_requires_exactly_one_source():
    with pytest.raises(SystemExit):
        cli._read("inline", "file.txt", label="prompt")  # both
    with pytest.raises(SystemExit):
        cli._read(None, None, label="prompt")  # neither
    assert cli._read("hi", None, label="prompt") == "hi"
