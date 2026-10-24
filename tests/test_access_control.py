"""Tests for is_whitelisted: True exactly on match, False otherwise."""

from __future__ import annotations

from cio_info_agent.interfaces.telegram_bot.access_control import is_whitelisted


def test_is_whitelisted_true_when_chat_id_matches() -> None:
    assert is_whitelisted(123456, 123456) is True


def test_is_whitelisted_false_when_chat_id_differs() -> None:
    assert is_whitelisted(111111, 123456) is False


def test_is_whitelisted_true_when_string_and_int_match() -> None:
    assert is_whitelisted("123456", 123456) is True


def test_is_whitelisted_false_when_string_and_int_differ() -> None:
    assert is_whitelisted("111111", 123456) is False


def test_is_whitelisted_false_when_incoming_is_none() -> None:
    assert is_whitelisted(None, 123456) is False


def test_is_whitelisted_false_when_configured_is_none() -> None:
    assert is_whitelisted(123456, None) is False


def test_is_whitelisted_false_when_both_are_none() -> None:
    assert is_whitelisted(None, None) is False


def test_is_whitelisted_false_when_incoming_has_whitespace_padding() -> None:
    assert is_whitelisted(" 123456", 123456) is False


def test_is_whitelisted_false_when_incoming_is_empty_string() -> None:
    assert is_whitelisted("", 123456) is False
