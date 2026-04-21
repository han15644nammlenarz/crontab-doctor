"""Tests for expression_diff and expression_diff_formatter."""
import pytest

from crontab_doctor.expression_diff import (
    diff_expressions,
    ExpressionDiff,
    FieldDiff,
)
from crontab_doctor.expression_diff_formatter import format_expression_diff


# ---------------------------------------------------------------------------
# diff_expressions
# ---------------------------------------------------------------------------

def test_identical_expressions_have_no_diffs():
    result = diff_expressions("0 * * * *", "0 * * * *")
    assert result.identical
    assert result.field_diffs == []
    assert result.error is None


def test_different_minute_field():
    result = diff_expressions("0 * * * *", "30 * * * *")
    assert not result.identical
    assert len(result.field_diffs) == 1
    assert result.field_diffs[0].field_name == "minute"
    assert result.field_diffs[0].left == "0"
    assert result.field_diffs[0].right == "30"


def test_multiple_field_differences():
    result = diff_expressions("0 6 * * 1", "30 12 * * 5")
    names = {d.field_name for d in result.field_diffs}
    assert "minute" in names
    assert "hour" in names
    assert "day_of_week" in names


def test_invalid_left_expression_returns_error():
    result = diff_expressions("bad expr", "0 * * * *")
    assert result.error is not None
    assert "left" in result.error.lower()


def test_invalid_right_expression_returns_error():
    result = diff_expressions("0 * * * *", "also bad")
    assert result.error is not None
    assert "right" in result.error.lower()


def test_summary_identical():
    result = diff_expressions("* * * * *", "* * * * *")
    assert "identical" in result.summary().lower()


def test_summary_with_diffs():
    result = diff_expressions("0 * * * *", "5 * * * *")
    summary = result.summary()
    assert "minute" in summary
    assert "->" in summary


def test_summary_with_error():
    result = diff_expressions("bad", "* * * * *")
    assert "Error" in result.summary()


def test_field_diff_repr():
    fd = FieldDiff("minute", "0", "30")
    assert "minute" in repr(fd)


# ---------------------------------------------------------------------------
# format_expression_diff
# ---------------------------------------------------------------------------

def test_format_identical_contains_checkmark():
    result = diff_expressions("0 * * * *", "0 * * * *")
    output = format_expression_diff(result, color=False)
    assert "identical" in output.lower()


def test_format_diff_contains_field_names():
    result = diff_expressions("0 6 * * *", "0 12 * * *")
    output = format_expression_diff(result, color=False)
    assert "hour" in output


def test_format_error_mentions_error():
    result = diff_expressions("bad", "* * * * *")
    output = format_expression_diff(result, color=False)
    assert "left" in output.lower() or "invalid" in output.lower()


def test_format_color_disabled_no_escape_codes():
    result = diff_expressions("0 * * * *", "5 * * * *")
    output = format_expression_diff(result, color=False)
    assert "\033[" not in output


def test_format_color_enabled_contains_escape_codes():
    result = diff_expressions("0 * * * *", "5 * * * *")
    output = format_expression_diff(result, color=True)
    assert "\033[" in output
