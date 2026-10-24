"""Tests for AppConfig: fail-fast behavior on missing required environment variables."""

from __future__ import annotations

import pytest

from cio_info_agent.infrastructure.config import AppConfig, MissingConfigError

REQUIRED_ENV_VARS = {
    "TELEGRAM_BOT_TOKEN": "dummy-token",
    "TELEGRAM_CHAT_ID": "123456",
    "LLM_API_KEY": "dummy-key",
}


def _set_all_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, value in REQUIRED_ENV_VARS.items():
        monkeypatch.setenv(name, value)


def test_from_env_succeeds_when_all_required_vars_are_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_all_env(monkeypatch)

    config = AppConfig.from_env()

    assert config.telegram_bot_token == "dummy-token"
    assert config.telegram_chat_id == "123456"
    assert config.llm_api_key == "dummy-key"


@pytest.mark.parametrize("missing_var", sorted(REQUIRED_ENV_VARS))
def test_from_env_raises_clear_exception_when_required_var_is_missing(
    monkeypatch: pytest.MonkeyPatch, missing_var: str
) -> None:
    _set_all_env(monkeypatch)
    monkeypatch.delenv(missing_var, raising=False)

    with pytest.raises(MissingConfigError) as excinfo:
        AppConfig.from_env()

    assert missing_var in str(excinfo.value)


@pytest.mark.parametrize("missing_var", sorted(REQUIRED_ENV_VARS))
def test_from_env_raises_clear_exception_when_required_var_is_empty_string(
    monkeypatch: pytest.MonkeyPatch, missing_var: str
) -> None:
    _set_all_env(monkeypatch)
    monkeypatch.setenv(missing_var, "")

    with pytest.raises(MissingConfigError) as excinfo:
        AppConfig.from_env()

    assert missing_var in str(excinfo.value)


@pytest.mark.parametrize("missing_var", sorted(REQUIRED_ENV_VARS))
def test_from_env_raises_clear_exception_when_required_var_is_whitespace_only(
    monkeypatch: pytest.MonkeyPatch, missing_var: str
) -> None:
    _set_all_env(monkeypatch)
    monkeypatch.setenv(missing_var, "   ")

    with pytest.raises(MissingConfigError) as excinfo:
        AppConfig.from_env()

    assert missing_var in str(excinfo.value)


def test_repr_never_exposes_secret_values(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_all_env(monkeypatch)

    config = AppConfig.from_env()

    rendered = repr(config)
    assert "dummy-token" not in rendered
    assert "dummy-key" not in rendered
