"""Tests for crontab_doctor.cron_quota."""
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

import pytest

from crontab_doctor.cron_quota import (
    QuotaResult,
    QuotaReport,
    check_quota,
)


# ---------------------------------------------------------------------------
# QuotaResult unit tests
# ---------------------------------------------------------------------------

def test_quota_result_ok_when_no_warnings():
    r = QuotaResult(expression="* * * * *", runs_in_window=1440,
                    window_hours=24, max_runs=None)
    assert r.ok() is True


def test_quota_result_not_ok_when_warnings():
    r = QuotaResult(expression="* * * * *", runs_in_window=1440,
                    window_hours=24, max_runs=100,
                    warnings=["exceeds per-expression limit of 100"])
    assert r.ok() is False


def test_quota_result_not_ok_when_error():
    r = QuotaResult(expression="bad", runs_in_window=0,
                    window_hours=24, max_runs=None, error="parse error")
    assert r.ok() is False


def test_quota_result_summary_ok():
    r = QuotaResult(expression="0 * * * *", runs_in_window=24,
                    window_hours=24, max_runs=None)
    s = r.summary()
    assert "0 * * * *" in s
    assert "24" in s
    assert "within quota" in s


def test_quota_result_summary_singular_run():
    r = QuotaResult(expression="0 0 * * *", runs_in_window=1,
                    window_hours=24, max_runs=None)
    assert "1 run " in r.summary()


def test_quota_result_summary_with_warning():
    r = QuotaResult(expression="* * * * *", runs_in_window=1440,
                    window_hours=24, max_runs=100,
                    warnings=["exceeds per-expression limit of 100"])
    assert "exceeds" in r.summary()


def test_quota_result_summary_error():
    r = QuotaResult(expression="bad", runs_in_window=0,
                    window_hours=24, max_runs=None, error="parse error")
    assert "ERROR" in r.summary()
    assert "parse error" in r.summary()


# ---------------------------------------------------------------------------
# QuotaReport unit tests
# ---------------------------------------------------------------------------

def test_quota_report_ok_all_clean():
    r1 = QuotaResult("0 * * * *", 24, 24, None)
    report = QuotaReport(results=[r1], total_runs=24)
    assert report.ok() is True


def test_quota_report_not_ok_when_global_warning():
    r1 = QuotaResult("0 * * * *", 24, 24, None)
    report = QuotaReport(results=[r1], total_runs=24, global_max=10,
                         global_warnings=["total 24 runs exceeds global limit of 10"])
    assert report.ok() is False


def test_quota_report_summary_empty():
    report = QuotaReport()
    assert report.summary() == "No expressions checked."


def test_quota_report_summary_includes_global_warning():
    r1 = QuotaResult("0 * * * *", 24, 24, None)
    report = QuotaReport(results=[r1], total_runs=24,
                         global_warnings=["total 24 runs exceeds global limit of 10"])
    s = report.summary()
    assert "Global" in s
    assert "exceeds" in s


# ---------------------------------------------------------------------------
# check_quota integration (mocked estimate_runs)
# ---------------------------------------------------------------------------

def _mock_est(count: int):
    m = MagicMock()
    m.ok.return_value = True
    m.error = None
    m.run_times = [object()] * count
    return m


def _mock_est_error(msg: str):
    m = MagicMock()
    m.ok.return_value = False
    m.error = msg
    m.run_times = []
    return m


@patch("crontab_doctor.cron_quota.estimate_runs")
def test_check_quota_no_limits(mock_est):
    mock_est.return_value = _mock_est(24)
    report = check_quota(["0 * * * *"], window_hours=24)
    assert report.ok() is True
    assert report.total_runs == 24


@patch("crontab_doctor.cron_quota.estimate_runs")
def test_check_quota_per_expression_exceeded(mock_est):
    mock_est.return_value = _mock_est(1440)
    report = check_quota(["* * * * *"], window_hours=24, max_runs_per_expression=100)
    assert report.ok() is False
    assert any("exceeds" in w for w in report.results[0].warnings)


@patch("crontab_doctor.cron_quota.estimate_runs")
def test_check_quota_global_exceeded(mock_est):
    mock_est.return_value = _mock_est(720)
    report = check_quota(
        ["*/2 * * * *", "*/2 * * * *"],
        window_hours=24,
        max_runs_total=1000,
    )
    assert report.total_runs == 1440
    assert report.ok() is False
    assert report.global_warnings


@patch("crontab_doctor.cron_quota.estimate_runs")
def test_check_quota_estimation_error(mock_est):
    mock_est.return_value = _mock_est_error("invalid expression")
    report = check_quota(["bad expr"])
    assert report.results[0].error == "invalid expression"
    assert report.ok() is False


@patch("crontab_doctor.cron_quota.estimate_runs")
def test_check_quota_window_hours_clamped(mock_est):
    mock_est.return_value = _mock_est(5)
    report = check_quota(["0 * * * *"], window_hours=0)
    # should not raise; window clamped to 1
    assert report.total_runs == 5
