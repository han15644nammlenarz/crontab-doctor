"""Tests for window_analyzer and window_formatter."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest

from crontab_doctor.window_analyzer import WindowResult, analyze_window
from crontab_doctor.window_formatter import format_window_result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIXED_NOW = datetime(2024, 6, 1, 12, 0)


# ---------------------------------------------------------------------------
# WindowResult unit tests
# ---------------------------------------------------------------------------

def test_window_result_ok_when_no_error():
    r = WindowResult(
        expression="* * * * *",
        window_start=FIXED_NOW,
        window_end=FIXED_NOW,
        fires=[],
    )
    assert r.ok() is True


def test_window_result_not_ok_when_error():
    r = WindowResult(
        expression="bad",
        window_start=FIXED_NOW,
        window_end=FIXED_NOW,
        error="parse error",
    )
    assert r.ok() is False


def test_window_result_summary_singular():
    end = datetime(2024, 6, 1, 13, 0)
    r = WindowResult(
        expression="0 * * * *",
        window_start=FIXED_NOW,
        window_end=end,
        fires=[datetime(2024, 6, 1, 12, 0)],
    )
    assert "1 time" in r.summary()
    assert "60 minutes" in r.summary()


def test_window_result_summary_plural():
    end = datetime(2024, 6, 1, 13, 0)
    fires = [datetime(2024, 6, 1, 12, i) for i in range(5)]
    r = WindowResult(
        expression="*/12 * * * *",
        window_start=FIXED_NOW,
        window_end=end,
        fires=fires,
    )
    assert "5 times" in r.summary()


def test_window_result_summary_error():
    r = WindowResult(
        expression="bad",
        window_start=FIXED_NOW,
        window_end=FIXED_NOW,
        error="invalid",
    )
    assert "Error" in r.summary()


# ---------------------------------------------------------------------------
# analyze_window integration tests (real next_runs)
# ---------------------------------------------------------------------------

def test_analyze_every_minute_fills_window():
    result = analyze_window("* * * * *", window_minutes=5, from_dt=FIXED_NOW)
    assert result.ok()
    assert len(result.fires) == 5


def test_analyze_hourly_fires_once_in_60_min_window():
    result = analyze_window("0 * * * *", window_minutes=60, from_dt=FIXED_NOW)
    assert result.ok()
    assert len(result.fires) == 1
    assert result.fires[0] == FIXED_NOW


def test_analyze_no_fires_in_narrow_window():
    # Expression fires at minute 30; window is only 10 min from :00
    result = analyze_window("30 * * * *", window_minutes=10, from_dt=FIXED_NOW)
    assert result.ok()
    assert len(result.fires) == 0


def test_analyze_invalid_expression_returns_error():
    result = analyze_window("99 99 99 99 99", window_minutes=60, from_dt=FIXED_NOW)
    assert not result.ok()
    assert result.error is not None


# ---------------------------------------------------------------------------
# format_window_result tests
# ---------------------------------------------------------------------------

def test_format_contains_expression():
    r = WindowResult(
        expression="0 9 * * 1",
        window_start=FIXED_NOW,
        window_end=datetime(2024, 6, 1, 13, 0),
        fires=[],
    )
    out = format_window_result(r, color=False)
    assert "0 9 * * 1" in out


def test_format_no_fires_shows_warning():
    r = WindowResult(
        expression="0 9 * * 1",
        window_start=FIXED_NOW,
        window_end=datetime(2024, 6, 1, 13, 0),
        fires=[],
    )
    out = format_window_result(r, color=False)
    assert "Does not fire" in out


def test_format_fires_listed():
    fires = [datetime(2024, 6, 1, 12, i) for i in range(3)]
    r = WindowResult(
        expression="* * * * *",
        window_start=FIXED_NOW,
        window_end=datetime(2024, 6, 1, 13, 0),
        fires=fires,
    )
    out = format_window_result(r, color=False)
    assert "3 firings" in out
    assert "2024-06-01 12:00" in out


def test_format_error_shown():
    r = WindowResult(
        expression="bad",
        window_start=FIXED_NOW,
        window_end=FIXED_NOW,
        error="parse error",
    )
    out = format_window_result(r, color=False)
    assert "parse error" in out
