"""Application configuration, sourced exclusively from environment variables (AD-8).

Secrets must never be hardcoded. Missing or blank required values fail fast with
a clear exception instead of silently falling back to defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


class MissingConfigError(RuntimeError):
    """Raised when a required environment variable is not set or is blank."""

    def __init__(self, env_var_name: str) -> None:
        super().__init__(
            f"Required environment variable '{env_var_name}' is not set."
        )
        self.env_var_name = env_var_name


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value or not value.strip():
        raise MissingConfigError(name)
    return value


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration loaded from environment variables.

    `repr=False` on every field keeps secrets out of the default `__repr__`
    (and therefore out of logs, prints, and tracebacks) — see AD-8.
    """

    telegram_bot_token: str = field(repr=False)
    telegram_chat_id: str = field(repr=False)
    llm_api_key: str = field(repr=False)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load the configuration from environment variables.

        Raises:
            MissingConfigError: if a required environment variable is missing
                or blank.
        """
        return cls(
            telegram_bot_token=_require_env("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=_require_env("TELEGRAM_CHAT_ID"),
            llm_api_key=_require_env("LLM_API_KEY"),
        )
