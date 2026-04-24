"""Tests for crontab_doctor.frequency_analyzer."""
import pytest

from crontab_doctor.frequency_analyzer import (
    FrequencyResult,
    _categorize,
    analyze_frequency,
    compare_frequencies,
)


# ---------------------------------------------------------------------------
# _categorize
# ---------------------------------------------------------------------------

def test_categorize_every_minute():
    assert _categorize(60 * 24) == "very_high"


def test_categorize_hourly():
    assert _categorize(24) == "high"


def test_categorize_daily():
    assert _categorize(1) == "medium"


def test_categorize_weekly():
    assert _categorize(1 / 7) == "low"


def test_categorize_monthly():
    assert _categorize(1 / 30) == "very_low"


# ---------------------------------------------------------------------------
# analyze_frequency — invalid expression
# ---------------------------------------------------------------------------

def test_analyze_invalid_expression_returns_error():
    result = analyze_frequency("not a cron")
    assert not result.ok()
    assert result.error is not None
    assert result.runs_per_day is None
    assert result.category == "unknown"


def test_analyze_invalid_expression_summary_contains_error():
    result = analyze_frequency("bad")
    assert "error" in result.summary().lower()


# ---------------------------------------------------------------------------
# analyze_frequency — valid expressions
# ---------------------------------------------------------------------------

def test_analyze_every_minute_is_very_high():
    result = analyze_frequency("* * * * *")
    assert result.ok()
    assert result.category == "very_high"
    assert result.runs_per_day is not None
    assert result.runs_per_day > 0


def test_analyze_every_minute_has_warning():
    result = analyze_frequency("* * * * *")
    assert any("frequently" in w.lower() for w in result.warnings)


def test_analyze_daily_midnight_is_medium():
    result = analyze_frequency("0 0 * * *")
    assert result.ok()
    assert result.category == "medium"


def test_analyze_runs_per_week_consistent_with_per_day():
    result = analyze_frequency("0 * * * *")  # hourly
    assert result.ok()
    assert abs(result.runs_per_week - result.runs_per_day * 7) < 0.01


def test_analyze_runs_per_month_consistent_with_per_day():
    result = analyze_frequency("0 * * * *")
    assert result.ok()
    assert abs(result.runs_per_month - result.runs_per_day * 30) < 0.01


def test_analyze_summary_contains_expression():
    result = analyze_frequency("0 0 * * *")
    assert "0 0 * * *" in result.summary()


# ---------------------------------------------------------------------------
# compare_frequencies
# ---------------------------------------------------------------------------

def test_compare_sorted_highest_first():
    exprs = ["0 0 * * *", "* * * * *", "0 * * * *"]
    results = compare_frequencies(exprs)
    rates = [r.runs_per_day for r in results if r.runs_per_day is not None]
    assert rates == sorted(rates, reverse=True)


def test_compare_invalid_expression_included_last():
    exprs = ["0 0 * * *", "not valid"]
    results = compare_frequencies(exprs)
    assert results[-1].expression == "not valid"
    assert not results[-1].ok()


def test_compare_returns_result_for_each_expression():
    exprs = ["* * * * *", "0 0 * * *", "0 12 * * 1"]
    results = compare_frequencies(exprs)
    assert len(results) == len(exprs)
