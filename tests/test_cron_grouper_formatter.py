"""Tests for cron_grouper and group_formatter."""
from __future__ import annotations

import pytest

from crontab_doctor.cron_grouper import GroupResult, group_expressions
from crontab_doctor.group_formatter import format_group_result


# ---------------------------------------------------------------------------
# GroupResult helpers
# ---------------------------------------------------------------------------

def test_group_result_ok_when_no_error():
    r = GroupResult(groups={"daily": ["0 0 * * *"]})
    assert r.ok() is True


def test_group_result_not_ok_when_error():
    r = GroupResult(error="bad strategy")
    assert r.ok() is False


def test_group_result_summary_error():
    r = GroupResult(error="bad strategy")
    assert "Error" in r.summary()


def test_group_result_summary_counts():
    r = GroupResult(groups={"daily": ["0 0 * * *", "30 6 * * *"], "hourly": ["0 * * * *"]})
    s = r.summary()
    assert "3" in s
    assert "2" in s  # two groups


def test_group_result_summary_ungrouped():
    r = GroupResult(groups={}, ungrouped=["NOT_VALID"])
    assert "ungrouped" in r.summary()


# ---------------------------------------------------------------------------
# group_expressions
# ---------------------------------------------------------------------------

def test_group_by_frequency_daily():
    result = group_expressions(["0 0 * * *", "30 6 * * *"], by="frequency")
    assert result.ok()
    # Both should land in the same frequency bucket
    assert any("daily" in k.lower() for k in result.groups)


def test_group_by_hour():
    result = group_expressions(["0 0 * * *", "30 0 * * *", "0 6 * * *"], by="hour")
    assert result.ok()
    assert "0" in result.groups
    assert len(result.groups["0"]) == 2


def test_group_by_minute():
    result = group_expressions(["0 * * * *", "0 6 * * *", "30 * * * *"], by="minute")
    assert result.ok()
    assert "0" in result.groups
    assert len(result.groups["0"]) == 2


def test_invalid_strategy_returns_error():
    result = group_expressions(["0 0 * * *"], by="weekday")
    assert not result.ok()
    assert "weekday" in result.error


def test_unparseable_expression_goes_to_ungrouped():
    result = group_expressions(["NOT_A_CRON"], by="frequency")
    assert result.ok()
    assert "NOT_A_CRON" in result.ungrouped


def test_empty_input_returns_empty_groups():
    result = group_expressions([], by="frequency")
    assert result.ok()
    assert result.groups == {}
    assert result.ungrouped == []


# ---------------------------------------------------------------------------
# format_group_result
# ---------------------------------------------------------------------------

def test_format_error_result_contains_error_text():
    r = GroupResult(error="unknown strategy")
    out = format_group_result(r, color=False)
    assert "unknown strategy" in out


def test_format_groups_contains_key():
    r = GroupResult(groups={"daily": ["0 0 * * *"]})
    out = format_group_result(r, color=False)
    assert "daily" in out


def test_format_groups_contains_expression():
    r = GroupResult(groups={"daily": ["0 0 * * *"]})
    out = format_group_result(r, color=False)
    assert "0 0 * * *" in out


def test_format_ungrouped_section_shown():
    r = GroupResult(groups={}, ungrouped=["BAD_EXPR"])
    out = format_group_result(r, color=False)
    assert "ungrouped" in out
    assert "BAD_EXPR" in out


def test_format_with_color_does_not_raise():
    r = GroupResult(groups={"hourly": ["0 * * * *"]})
    out = format_group_result(r, color=True)
    assert "0 * * * *" in out
