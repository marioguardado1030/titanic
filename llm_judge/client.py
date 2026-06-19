"""Thin wrapper around the Anthropic SDK for structured judge calls.

Centralizes model selection, thinking/effort configuration, and structured-output
parsing so the evaluators stay focused on prompt construction and aggregation.

Defaults follow current Anthropic guidance: Claude Opus 4.8 as the model, adaptive
thinking on (it improves evaluation reliability), and structured outputs via
``messages.parse`` so responses come back as validated Pydantic instances.

Using a *different* model for evaluation than for generation is the recommended
way to avoid self-enhancement bias; the model is therefore a first-class,
per-call-overridable setting.
"""

from __future__ import annotations

from typing import Optional, Type, TypeVar

import anthropic
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = "claude-opus-4-8"


class JudgeClient:
    """Wraps an Anthropic client and returns parsed, schema-validated results."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        effort: str = "high",
        thinking: bool = True,
        max_tokens: int = 8000,
        client: Optional[anthropic.Anthropic] = None,
    ) -> None:
        # `anthropic.Anthropic()` resolves credentials from the environment
        # (ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN / an `ant auth login` profile).
        self._client = client or anthropic.Anthropic()
        self.model = model
        self.effort = effort
        self.thinking = thinking
        self.max_tokens = max_tokens

    def parse(
        self,
        *,
        system: str,
        prompt: str,
        schema: Type[T],
        model: Optional[str] = None,
    ) -> T:
        """Run one structured judge call and return a validated ``schema`` instance.

        Adaptive thinking and the effort level are applied automatically. The
        response is constrained to ``schema`` via structured outputs, so the
        returned object is already validated.
        """
        kwargs: dict = {
            "model": model or self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
            "output_format": schema,
            "output_config": {"effort": self.effort},
        }
        if self.thinking:
            kwargs["thinking"] = {"type": "adaptive"}

        response = self._client.messages.parse(**kwargs)

        parsed = response.parsed_output
        if parsed is None:
            # Happens on refusal or truncation — surface a clear, actionable error.
            raise JudgeError(
                f"Judge returned no parseable output "
                f"(stop_reason={response.stop_reason!r}). "
                "Check for a refusal or raise max_tokens."
            )
        return parsed


class JudgeError(RuntimeError):
    """Raised when a judge call cannot produce a usable structured result."""
