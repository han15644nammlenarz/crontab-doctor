"""Tests for cron_similarity and similarity_formatter."""
import pytest

from crontab_doctor.cron_similarity import (
    SimilarityResult,
    _field_similarity,
    _similarity_label,
    compare_expressions,
)
from crontab_doctor.similarity_formatter import format_similarity, format_similarity_list


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------

def test_field_similarity_identical_sets():
    assert _field_similarity({1, 2, 3}, {1, 2, 3}) == 1.0


def test_field_similarity_disjoint_sets():
    assert _field_similarity({1, 2}, {3, 4}) == 0.0


def test_field_similarity_partial_overlap():
    score = _field_similarity({1, 2, 3}, {2, 3, 4})
    assert 0 < score < 1


def test_field_similarity_empty_both():
    assert _field_similarity(set(), set()) == 1.0


def test_similarity_label_boundaries():
    assert _similarity_label(1.0) == "nearly identical"
    assert _similarity_label(0.75) == "very similar"
    assert _similarity_label(0.55) == "moderately similar"
    assert _similarity_label(0.3) == "slightly similar"
    assert _similarity_label(0.1) == "dissimilar"


# ---------------------------------------------------------------------------
# compare_expressions
# ---------------------------------------------------------------------------

def test_identical_expressions_score_one():
    result = compare_expressions("0 * * * *", "0 * * * *")
    assert result.ok
    assert result.score == pytest.approx(1.0)


def test_completely_different_expressions_low_score():
    result = compare_expressions("0 0 1 1 0", "30 12 15 6 5")
    assert result.ok
    assert result.score < 0.3


def test_compare_returns_five_field_scores():
    result = compare_expressions("*/5 * * * *", "*/10 * * * *")
    assert result.ok
    assert len(result.field_scores) == 5


def test_compare_invalid_left_returns_error():
    result = compare_expressions("bad expression", "0 * * * *")
    assert not result.ok
    assert "Left" in result.error


def test_compare_invalid_right_returns_error():
    result = compare_expressions("0 * * * *", "not valid")
    assert not result.ok
    assert "Right" in result.error


def test_summary_contains_percentage():
    result = compare_expressions("0 * * * *", "0 * * * *")
    assert "100%" in result.summary()


def test_summary_error_message():
    result = compare_expressions("bad", "0 * * * *")
    assert result.summary().startswith("Error:")


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def test_format_similarity_contains_field_names():
    result = compare_expressions("0 * * * *", "0 * * * *")
    output = format_similarity(result, color=False)
    for name in ("minute", "hour", "dom", "month", "dow"):
        assert name in output


def test_format_similarity_error_result():
    result = SimilarityResult("bad", "0 * * * *", 0.0, error="Left expression: oops")
    output = format_similarity(result, color=False)
    assert "oops" in output


def test_format_similarity_list_empty():
    output = format_similarity_list([], color=False)
    assert "No comparisons" in output


def test_format_similarity_list_multiple():
    r1 = compare_expressions("0 * * * *", "0 * * * *")
    r2 = compare_expressions("*/5 * * * *", "*/10 * * * *")
    output = format_similarity_list([r1, r2], color=False)
    assert output.count("Similarity:") == 2
