"""Access control for the Telegram bot: whitelist check by chat ID (FR10)."""

from __future__ import annotations


def is_whitelisted(
    incoming_chat_id: str | int | None, configured_chat_id: str | int | None
) -> bool:
    """Decide whether an incoming chat ID is allowed to interact with the bot.

    Pure decision function: returns True only if both chat IDs are present
    and the incoming chat ID exactly matches the configured chat ID. `None`
    never matches, even against another `None` — a missing chat ID can never
    be a valid grant of access.

    Args:
        incoming_chat_id: The chat ID of the incoming message.
        configured_chat_id: The chat ID configured as whitelisted.

    Returns:
        True if both chat IDs are present and match, else False.
    """
    if incoming_chat_id is None or configured_chat_id is None:
        return False
    return str(incoming_chat_id) == str(configured_chat_id)
