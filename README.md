# CIONewsTicker — CIO Info Agent

Telegram bot that delivers a daily, relevance-filtered news briefing to a
single CIO, curated from public RSS feeds and scored by an LLM. See
[`_bmad-output/planning-artifacts/`](_bmad-output/planning-artifacts) for the
product brief, PRD, domain model, and architecture spine that drive this
implementation.

## Setup

Requires Python 3.12+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
```

### Required environment variables

| Variable | Purpose |
|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token (from [@BotFather](https://t.me/BotFather)) |
| `TELEGRAM_CHAT_ID` | The single whitelisted chat ID allowed to use the bot |
| `LLM_API_KEY` | API key for the configured LLM provider |

Export these in your shell before running the app or the tests that need
them. The app never falls back to a default — a missing or blank value fails
fast with a clear error (`MissingConfigError`).

## Running the tests

```bash
uv run pytest
```

