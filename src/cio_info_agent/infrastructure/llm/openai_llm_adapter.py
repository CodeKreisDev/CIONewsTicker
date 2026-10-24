"""LLMPort implementation using the OpenAI-compatible chat completions API.

Model defaults to the cost-efficient small-tier model the Architecture Spine
(AD-6) recommends for this system's budget (NFR1). The concrete client is
injectable so tests never need a real API key or network access.
"""

from __future__ import annotations

import re

import openai
from openai import OpenAI

from cio_info_agent.application.ports.llm_port import (
    LLMAntwortUngueltigError,
    LLMNichtErreichbarError,
)

_STANDARD_MODELL = "gpt-5.6-luna"
_ANFRAGE_TIMEOUT_SECONDS = 10

_SYSTEM_PROMPT = (
    "You are a relevance-scoring assistant for a CIO in the real estate "
    "investment sector, with responsibilities spanning enterprise IT, "
    "security, ESG regulation, and PropTech. Given an article's title and "
    "description, respond with ONLY a single integer from 1 to 10 rating "
    "its relevance to this persona — 10 being critical (e.g. a severe "
    "security advisory), 1 being irrelevant. Respond with nothing but the "
    "number."
)

# Prefer an explicit "X/10" occurrence (a common model habit, and the
# clearest signal of the model's actual verdict even when it pads its
# answer with other text/numbers first). The negative lookaround on both
# patterns excludes a digit that is part of a longer integer (e.g. the "10"
# inside "100") or a decimal number (e.g. "7.5"), which must be rejected as
# an invalid response rather than silently truncated.
_SKALA_PATTERN = re.compile(r"(?<![.\d])(10|[1-9])\s*/\s*10\b")
_ZAHL_PATTERN = re.compile(r"(?<![.\d])(10|[1-9])(?![.\d])")


class OpenAILLMAdapter:
    """Scores Artikel relevance via an OpenAI-compatible chat model."""

    def __init__(self, api_key: str, modell: str = _STANDARD_MODELL, client: object | None = None) -> None:
        self._modell = modell
        self._client = client or OpenAI(api_key=api_key, timeout=_ANFRAGE_TIMEOUT_SECONDS)

    def bewerte_relevanz(self, titel: str, beschreibung: str) -> int:
        """Score an Artikel's relevance via the configured chat model.

        Raises:
            LLMNichtErreichbarError: if the API call fails (network, auth,
                rate limit, server error — any `openai.OpenAIError`).
            LLMAntwortUngueltigError: if the response is empty, contains no
                usable number, or a number outside the valid 1-10 range (a
                single malformed response must never crash the whole
                scoring run — only this one Artikel is affected).
        """
        nutzer_prompt = f"Title: {titel}\nDescription: {beschreibung}"
        try:
            antwort = self._client.chat.completions.create(
                model=self._modell,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": nutzer_prompt},
                ],
            )
        except openai.OpenAIError as exc:
            raise LLMNichtErreichbarError(f"LLM request failed: {exc}") from exc

        if not antwort.choices:
            # A real, documented OpenAI behavior (e.g. content filtering)
            # that must be treated as "no usable score", not crash the run.
            raise LLMAntwortUngueltigError("LLM response contained no choices.")

        inhalt = antwort.choices[0].message.content or ""
        return self._parse_score(inhalt)

    @staticmethod
    def _parse_score(inhalt: str) -> int:
        skalen_treffer = _SKALA_PATTERN.search(inhalt)
        if skalen_treffer is not None:
            return int(skalen_treffer.group(1))

        treffer = _ZAHL_PATTERN.search(inhalt)
        if treffer is None:
            raise LLMAntwortUngueltigError(f"LLM response contained no valid 1-10 number: {inhalt!r}")
        return int(treffer.group(1))
