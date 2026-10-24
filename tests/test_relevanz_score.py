"""Tests for RelevanzScore: value-range validation and the relevance threshold."""

from __future__ import annotations

import pytest

from cio_info_agent.domain.artikel.exception.ungueltiger_relevanz_score_error import (
    UngueltigerRelevanzScoreError,
)
from cio_info_agent.domain.artikel.relevanz_score import RelevanzScore


@pytest.mark.parametrize("wert", [1, 5, 7, 10])
def test_accepts_values_within_range(wert: int) -> None:
    score = RelevanzScore(wert)
    assert score.wert == wert


@pytest.mark.parametrize("wert", [0, -1, 11, 100])
def test_rejects_values_outside_range(wert: int) -> None:
    with pytest.raises(UngueltigerRelevanzScoreError):
        RelevanzScore(wert)


@pytest.mark.parametrize("wert", [7, 8, 10])
def test_ist_relevant_true_at_or_above_threshold(wert: int) -> None:
    assert RelevanzScore(wert).ist_relevant() is True


@pytest.mark.parametrize("wert", [1, 5, 6])
def test_ist_relevant_false_below_threshold(wert: int) -> None:
    assert RelevanzScore(wert).ist_relevant() is False
