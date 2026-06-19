"""Rubric generation.

Well-defined rubrics reduce evaluation variance substantially versus open-ended
scoring. This generates a domain-specific rubric — one level per score, observable
characteristics, edge cases, and scoring guidelines — that can be attached to a
``Criterion`` and reused across evaluations.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from .client import JudgeClient
from .models import EdgeCase, Rubric, RubricLevel, Strictness
from .prompts import RUBRIC_SYSTEM, build_rubric_prompt


class _RubricResponse(BaseModel):
    levels: list[RubricLevel]
    edge_cases: list[EdgeCase] = []
    scoring_guidelines: list[str] = []


class RubricGenerator:
    def __init__(self, client: Optional[JudgeClient] = None) -> None:
        self.client = client or JudgeClient()

    def generate(
        self,
        criterion_name: str,
        criterion_description: str,
        *,
        domain: str = "general",
        scale_min: int = 1,
        scale_max: int = 5,
        strictness: Strictness = Strictness.BALANCED,
    ) -> Rubric:
        user_prompt = build_rubric_prompt(
            criterion_name,
            criterion_description,
            domain,
            scale_min,
            scale_max,
            strictness,
        )
        raw = self.client.parse(
            system=RUBRIC_SYSTEM, prompt=user_prompt, schema=_RubricResponse
        )
        return Rubric(
            criterion_name=criterion_name,
            scale_min=scale_min,
            scale_max=scale_max,
            strictness=strictness,
            levels=raw.levels,
            edge_cases=raw.edge_cases,
            scoring_guidelines=raw.scoring_guidelines,
        )
