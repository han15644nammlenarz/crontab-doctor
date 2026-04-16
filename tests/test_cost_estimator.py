"""Tests for cost_estimator and cli_cost."""
from unittest.mock import patch, MagicMock
import pytest
from crontab_doctor.cost_estimator import estimate_cost, CostEstimate


def _mock_est(run_times, error=None):
    m = MagicMock()
    m.ok.return_value = error is None
    m.run_times = run_times
    m.error = error
    return m


@patch("crontab_doctor.cost_estimator.estimate_runs")
def test_estimate_cost_ok(mock_er):
    mock_er.return_value = _mock_est([1, 2, 3])  # 3 runs in window
    result = estimate_cost("0 * * * *", cost_per_run=2.0)
    assert result.ok()
    assert result.runs_per_day == 3
    assert result.total_daily_cost == pytest.approx(6.0)
    assert result.total_monthly_cost == pytest.approx(180.0)


@patch("crontab_doctor.cost_estimator.estimate_runs")
def test_estimate_cost_error_propagates(mock_er):
    mock_er.return_value = _mock_est([], error="parse error")
    result = estimate_cost("bad expr")
    assert not result.ok()
    assert "parse error" in result.error
    assert result.runs_per_day == 0


@patch("crontab_doctor.cost_estimator.estimate_runs")
def test_high_frequency_warning(mock_er):
    mock_er.return_value = _mock_est(list(range(300)))
    result = estimate_cost("* * * * *")
    assert any("high frequency" in w for w in result.warnings)


@patch("crontab_doctor.cost_estimator.estimate_runs")
def test_high_cost_warning(mock_er):
    mock_er.return_value = _mock_est(list(range(200)))
    result = estimate_cost("*/5 * * * *", cost_per_run=10.0)
    assert any("Daily cost" in w for w in result.warnings)


@patch("crontab_doctor.cost_estimator.estimate_runs")
def test_no_warnings_for_normal_schedule(mock_er):
    mock_er.return_value = _mock_est(list(range(24)))
    result = estimate_cost("0 * * * *", cost_per_run=1.0)
    assert result.warnings == []


@patch("crontab_doctor.cost_estimator.estimate_runs")
def test_summary_contains_expression(mock_er):
    mock_er.return_value = _mock_est([1, 2])
    result = estimate_cost("0 9 * * 1")
    s = result.summary()
    assert "0 9 * * 1" in s
    assert "Runs/day" in s


@patch("crontab_doctor.cost_estimator.estimate_runs")
def test_summary_error(mock_er):
    mock_er.return_value = _mock_est([], error="bad")
    result = estimate_cost("x")
    assert "ERROR" in result.summary()


def test_cost_estimate_dataclass_defaults():
    ce = CostEstimate(
        expression="* * * * *",
        runs_per_day=1440,
        runs_per_month=43200,
        cost_per_run=0.5,
        total_daily_cost=720.0,
        total_monthly_cost=21600.0,
    )
    assert ce.ok()
    assert ce.warnings == []
    assert ce.error is None
