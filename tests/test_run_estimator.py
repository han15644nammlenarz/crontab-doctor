"""Tests for run_estimator module and its CLI command."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest

from crontab_doctor.run_estimator import estimate_runs, RunEstimate


BASE = datetime(2024, 6, 1, 0, 0)  # midnight, Saturday


# ---------------------------------------------------------------------------
# RunEstimate helpers
# ---------------------------------------------------------------------------

def test_run_estimate_ok_when_no_error():
    r = RunEstimate(expression="* * * * *", window_hours=1, count=60,
                    first_run=BASE, last_run=BASE)
    assert r.ok() is True


def test_run_estimate_not_ok_when_error():
    r = RunEstimate(expression="bad", window_hours=1, count=0,
                    first_run=None, last_run=None, error="parse error")
    assert r.ok() is False


def test_run_estimate_summary_error():
    r = RunEstimate(expression="bad", window_hours=1, count=0,
                    first_run=None, last_run=None, error="parse error")
    assert "Error" in r.summary()


def test_run_estimate_summary_never():
    r = RunEstimate(expression="0 3 31 2 *", window_hours=24, count=0,
                    first_run=None, last_run=None)
    assert "Never" in r.summary()


def test_run_estimate_summary_singular():
    dt = datetime(2024, 6, 1, 3, 0)
    r = RunEstimate(expression="0 3 * * *", window_hours=24, count=1,
                    first_run=dt, last_run=dt)
    assert "1 time" in r.summary()


def test_run_estimate_summary_plural():
    dt = datetime(2024, 6, 1, 0, 0)
    r = RunEstimate(expression="* * * * *", window_hours=1, count=60,
                    first_run=dt, last_run=dt)
    assert "60 times" in r.summary()


# ---------------------------------------------------------------------------
# estimate_runs logic
# ---------------------------------------------------------------------------

def test_estimate_invalid_window():
    result = estimate_runs("* * * * *", window_hours=0, from_dt=BASE)
    assert not result.ok()
    assert "positive" in result.error


def test_estimate_invalid_expression():
    result = estimate_runs("not a cron", window_hours=1, from_dt=BASE)
    assert not result.ok()
    assert result.count == 0


def test_estimate_every_minute_one_hour():
    result = estimate_runs("* * * * *", window_hours=1, from_dt=BASE)
    assert result.ok()
    assert result.count == 60
    assert result.first_run == BASE


def test_estimate_hourly_in_24h_window():
    result = estimate_runs("0 * * * *", window_hours=24, from_dt=BASE)
    assert result.ok()
    assert result.count == 24


def test_estimate_daily_at_midnight_in_24h_window():
    result = estimate_runs("0 0 * * *", window_hours=24, from_dt=BASE)
    assert result.ok()
    # BASE is midnight, so first fire is at BASE itself
    assert result.count == 1
    assert result.first_run == BASE


def test_estimate_first_and_last_run_populated():
    result = estimate_runs("0 * * * *", window_hours=3, from_dt=BASE)
    assert result.ok()
    assert result.first_run is not None
    assert result.last_run is not None
    assert result.last_run >= result.first_run


def test_estimate_uses_now_when_from_dt_none():
    """Smoke-test: calling without from_dt should not raise."""
    result = estimate_runs("0 * * * *", window_hours=1)
    assert result.ok()


def test_estimate_next_run_error_propagated():
    with patch("crontab_doctor.run_estimator.next_runs",
               side_effect=Exception("boom")):
        result = estimate_runs("* * * * *", window_hours=1, from_dt=BASE)
    # parse succeeds but next_runs raises — should surface as error
    assert not result.ok()
