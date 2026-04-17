"""Tests for crontab_doctor.alert_threshold."""
import datetime
from unittest.mock import patch, MagicMock
import pytest
from crontab_doctor.alert_threshold import check_threshold, ThresholdResult


def _mock_est(run_count=None, error=None):
    m = MagicMock()
    m.ok.return_value = error is None
    m.run_count = run_count
    m.error = error
    return m


@patch("crontab_doctor.alert_threshold.estimate_runs")
def test_estimation_error_propagates(mock_est):
    mock_est.return_value = _mock_est(error="parse error")
    result = check_threshold("bad expr", hours=24)
    assert not result.ok()
    assert "parse error" in result.errors[0]


@patch("crontab_doctor.alert_threshold.estimate_runs")
def test_no_warnings_when_within_thresholds(mock_est):
    mock_est.return_value = _mock_est(run_count=10)
    result = check_threshold("0 * * * *", hours=24, min_runs=5, max_runs=30)
    assert result.ok()
    assert result.warnings == []
    assert result.actual_runs == 10


@patch("crontab_doctor.alert_threshold.estimate_runs")
def test_warn_when_below_min(mock_est):
    mock_est.return_value = _mock_est(run_count=2)
    result = check_threshold("0 0 * * 0", hours=24, min_runs=5)
    assert result.ok()
    assert any("below minimum" in w for w in result.warnings)


@patch("crontab_doctor.alert_threshold.estimate_runs")
def test_warn_when_above_max(mock_est):
    mock_est.return_value = _mock_est(run_count=1500)
    result = check_threshold("* * * * *", hours=24, max_runs=100)
    assert result.ok()
    assert any("exceeds maximum" in w for w in result.warnings)


@patch("crontab_doctor.alert_threshold.estimate_runs")
def test_no_thresholds_no_warnings(mock_est):
    mock_est.return_value = _mock_est(run_count=60)
    result = check_threshold("0 * * * *", hours=24)
    assert result.ok()
    assert result.warnings == []


@patch("crontab_doctor.alert_threshold.estimate_runs")
def test_summary_ok(mock_est):
    mock_est.return_value = _mock_est(run_count=24)
    result = check_threshold("0 * * * *", hours=24, min_runs=1, max_runs=50)
    s = result.summary()
    assert "0 * * * *" in s
    assert "24" in s
    assert "satisfied" in s


@patch("crontab_doctor.alert_threshold.estimate_runs")
def test_summary_error(mock_est):
    mock_est.return_value = _mock_est(error="bad")
    result = check_threshold("bad", hours=24)
    s = result.summary()
    assert "ERROR" in s


@patch("crontab_doctor.alert_threshold.estimate_runs")
def test_summary_with_warning(mock_est):
    mock_est.return_value = _mock_est(run_count=1)
    result = check_threshold("0 0 1 1 *", hours=24, min_runs=5)
    s = result.summary()
    assert "WARN" in s
