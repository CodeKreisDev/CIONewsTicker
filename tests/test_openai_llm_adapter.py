"""Tests for OpenAILLMAdapter against a fully mocked OpenAI client (no network)."""

from __future__ import annotations

import openai
import pytest

from cio_info_agent.application.ports.llm_port import LLMAntwortUngueltigError, LLMNichtErreichbarError
from cio_info_agent.infrastructure.llm.openai_llm_adapter import OpenAILLMAdapter


class _FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = _FakeMessage(content)


class _FakeResponse:
    def __init__(self, content: str, leere_choices: bool = False) -> None:
        self.choices = [] if leere_choices else [_FakeChoice(content)]


class _FakeCompletions:
    def __init__(
        self,
        content: str | None = None,
        exception: Exception | None = None,
        leere_choices: bool = False,
    ) -> None:
        self._content = content
        self._exception = exception
        self._leere_choices = leere_choices
        self.letzter_aufruf: dict | None = None

    def create(self, model: str, messages: list[dict]) -> _FakeResponse:
        self.letzter_aufruf = {"model": model, "messages": messages}
        if self._exception is not None:
            raise self._exception
        return _FakeResponse(self._content or "", leere_choices=self._leere_choices)


class _FakeChat:
    def __init__(self, completions: _FakeCompletions) -> None:
        self.completions = completions


class _FakeClient:
    def __init__(
        self,
        content: str | None = None,
        exception: Exception | None = None,
        leere_choices: bool = False,
    ) -> None:
        self.completions = _FakeCompletions(content=content, exception=exception, leere_choices=leere_choices)
        self.chat = _FakeChat(self.completions)


def test_bewerte_relevanz_parses_plain_number() -> None:
    client = _FakeClient(content="8")
    adapter = OpenAILLMAdapter(api_key="unused", client=client)

    assert adapter.bewerte_relevanz("Title", "Description") == 8


def test_bewerte_relevanz_parses_number_with_surrounding_text() -> None:
    client = _FakeClient(content="Score: 8/10")
    adapter = OpenAILLMAdapter(api_key="unused", client=client)

    assert adapter.bewerte_relevanz("Title", "Description") == 8


def test_bewerte_relevanz_raises_when_response_has_no_number() -> None:
    client = _FakeClient(content="I cannot determine a score.")
    adapter = OpenAILLMAdapter(api_key="unused", client=client)

    with pytest.raises(LLMAntwortUngueltigError):
        adapter.bewerte_relevanz("Title", "Description")


def test_bewerte_relevanz_raises_when_score_out_of_range() -> None:
    client = _FakeClient(content="15")
    adapter = OpenAILLMAdapter(api_key="unused", client=client)

    with pytest.raises(LLMAntwortUngueltigError):
        adapter.bewerte_relevanz("Title", "Description")


def test_bewerte_relevanz_wraps_openai_errors() -> None:
    client = _FakeClient(exception=openai.APIConnectionError(request=None))
    adapter = OpenAILLMAdapter(api_key="unused", client=client)

    with pytest.raises(LLMNichtErreichbarError):
        adapter.bewerte_relevanz("Title", "Description")


def test_bewerte_relevanz_sends_title_and_description_to_the_model() -> None:
    client = _FakeClient(content="5")
    adapter = OpenAILLMAdapter(api_key="unused", modell="custom-model", client=client)

    adapter.bewerte_relevanz("My Title", "My Description")

    aufruf = client.completions.letzter_aufruf
    assert aufruf is not None
    assert aufruf["model"] == "custom-model"
    gesendeter_text = " ".join(m["content"] for m in aufruf["messages"])
    assert "My Title" in gesendeter_text
    assert "My Description" in gesendeter_text


def test_bewerte_relevanz_raises_on_empty_choices() -> None:
    client = _FakeClient(leere_choices=True)
    adapter = OpenAILLMAdapter(api_key="unused", client=client)

    with pytest.raises(LLMAntwortUngueltigError):
        adapter.bewerte_relevanz("Title", "Description")


def test_bewerte_relevanz_rejects_decimal_response() -> None:
    client = _FakeClient(content="7.5")
    adapter = OpenAILLMAdapter(api_key="unused", client=client)

    with pytest.raises(LLMAntwortUngueltigError):
        adapter.bewerte_relevanz("Title", "Description")


def test_bewerte_relevanz_extracts_the_x_of_10_score_not_an_unrelated_digit() -> None:
    # Regression test: an embedded unrelated digit (here, in "GPT-4") must
    # not be mistaken for the actual score when an explicit "X/10" is present.
    client = _FakeClient(content="GPT-4 rates this 9/10")
    adapter = OpenAILLMAdapter(api_key="unused", client=client)

    assert adapter.bewerte_relevanz("Title", "Description") == 9
