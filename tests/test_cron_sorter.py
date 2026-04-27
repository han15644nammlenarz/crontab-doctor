"""Tests for crontab_doctor.cron_sorter and sort_formatter."""
from __future__ import annotations

import pytest
from crontab_doctor.cron_sorter import sort_expressions, SortEntry, SortResult, VALID_KEYS
from crontab_doctor.sort_formatter import format_sort_result


# ---------------------------------------------------------------------------
# SortResult helpers
# ---------------------------------------------------------------------------

def test_sort_result_ok_when_no_error():
    r = SortResult(entries=[], sort_by="expression")
    assert r.ok() is True


def test_sort_result_not_ok_when_error():
    r = SortResult(error="boom")
    assert r.ok() is False


def test_sort_result_summary_error():
    r = SortResult(error="bad key")
    assert "Sort error" in r.summary()


def test_sort_result_summary_ok():
    entries = [SortEntry(expression="* * * * *", rank=1, sort_key="every-minute")]
    r = SortResult(entries=entries, sort_by="frequency")
    assert "1 expression(s)" in r.summary()
    assert "frequency" in r.summary()


def test_sort_result_summary_with_invalid():
    good = SortEntry(expression="0 * * * *", rank=1, sort_key="hourly")
    bad = SortEntry(expression="bad", rank=2, error="parse error")
    r = SortResult(entries=[good, bad], sort_by="expression")
    assert "1 skipped" in r.summary()


# ---------------------------------------------------------------------------
# sort_expressions
# ---------------------------------------------------------------------------

def test_invalid_sort_key_returns_error():
    result = sort_expressions(["* * * * *"], sort_by="foobar")
    assert not result.ok()
    assert "foobar" in result.error


def test_mismatched_labels_returns_error():
    result = sort_expressions(["* * * * *", "0 * * * *"], labels=["only-one"])
    assert not result.ok()
    assert "labels" in result.error.lower()


def test_sort_by_expression_orders_lexicographically():
    exprs = ["5 * * * *", "0 * * * *", "3 * * * *"]
    result = sort_expressions(exprs, sort_by="expression")
    assert result.ok()
    sorted_exprs = [e.expression for e in result.entries if not e.error]
    assert sorted_exprs == sorted(exprs)


def test_sort_by_expression_reverse():
    exprs = ["5 * * * *", "0 * * * *", "3 * * * *"]
    result = sort_expressions(exprs, sort_by="expression", reverse=True)
    assert result.ok()
    sorted_exprs = [e.expression for e in result.entries if not e.error]
    assert sorted_exprs == sorted(exprs, reverse=True)


def test_invalid_expression_placed_at_end():
    exprs = ["0 * * * *", "not-valid"]
    result = sort_expressions(exprs, sort_by="expression")
    assert result.ok()
    assert result.entries[-1].expression == "not-valid"
    assert result.entries[-1].error is not None


def test_labels_attached_to_entries():
    exprs = ["0 * * * *", "0 0 * * *"]
    labels = ["hourly-job", "daily-job"]
    result = sort_expressions(exprs, sort_by="label", labels=labels)
    assert result.ok()
    label_map = {e.expression: e.label for e in result.entries}
    assert label_map["0 * * * *"] == "hourly-job"
    assert label_map["0 0 * * *"] == "daily-job"


def test_ranks_are_sequential():
    exprs = ["0 * * * *", "0 0 * * *", "* * * * *"]
    result = sort_expressions(exprs, sort_by="expression")
    ranks = [e.rank for e in result.entries]
    assert ranks == list(range(1, len(exprs) + 1))


def test_sort_by_frequency_returns_result():
    exprs = ["* * * * *", "0 0 * * *"]
    result = sort_expressions(exprs, sort_by="frequency")
    assert result.ok()
    assert len(result.entries) == 2


def test_valid_keys_constant():
    assert "frequency" in VALID_KEYS
    assert "next_run" in VALID_KEYS
    assert "expression" in VALID_KEYS
    assert "label" in VALID_KEYS


# ---------------------------------------------------------------------------
# format_sort_result
# ---------------------------------------------------------------------------

def test_format_error_result_contains_error():
    r = SortResult(error="invalid key")
    out = format_sort_result(r, use_color=False)
    assert "Error" in out
    assert "invalid key" in out


def test_format_ok_result_contains_sort_by():
    r = sort_expressions(["0 * * * *"], sort_by="expression")
    out = format_sort_result(r, use_color=False)
    assert "expression" in out


def test_format_ok_result_contains_expression():
    r = sort_expressions(["0 0 * * *"], sort_by="expression")
    out = format_sort_result(r, use_color=False)
    assert "0 0 * * *" in out


def test_format_result_with_invalid_shows_error_marker():
    r = sort_expressions(["bad-expr"], sort_by="expression")
    out = format_sort_result(r, use_color=False)
    assert "!!" in out


def test_format_result_no_color_has_no_escape():
    r = sort_expressions(["0 * * * *"], sort_by="expression")
    out = format_sort_result(r, use_color=False)
    assert "\033[" not in out
