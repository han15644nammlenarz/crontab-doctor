"""Tests for anomaly_detector and anomaly_formatter."""
import pytest

from crontab_doctor.anomaly_detector import (
    AnomalyWarning,
    AnomalyResult,
    detect_anomalies,
)
from crontab_doctor.anomaly_formatter import (
    format_anomaly_warning,
    format_anomaly_result,
    format_anomaly_results,
)


# ---------------------------------------------------------------------------
# AnomalyWarning
# ---------------------------------------------------------------------------

def test_anomaly_warning_repr():
    w = AnomalyWarning(code="X", message="msg", severity="info")
    assert "X" in repr(w)
    assert "info" in repr(w)


def test_anomaly_warning_default_severity():
    w = AnomalyWarning(code="C", message="m")
    assert w.severity == "warning"


# ---------------------------------------------------------------------------
# AnomalyResult
# ---------------------------------------------------------------------------

def test_anomaly_result_ok_when_no_error():
    r = AnomalyResult(expression="* * * * *")
    assert r.ok is True


def test_anomaly_result_not_ok_when_error():
    r = AnomalyResult(expression="bad", error="parse failed")
    assert r.ok is False


def test_anomaly_result_summary_no_warnings():
    r = AnomalyResult(expression="0 * * * *")
    assert "No anomalies" in r.summary()


def test_anomaly_result_summary_with_warnings():
    w = AnomalyWarning(code="TEST", message="test msg", severity="warning")
    r = AnomalyResult(expression="0 * * * *", warnings=[w])
    s = r.summary()
    assert "TEST" in s
    assert "test msg" in s


def test_anomaly_result_summary_error():
    r = AnomalyResult(expression="bad", error="something broke")
    assert "ERROR" in r.summary()
    assert "something broke" in r.summary()


# ---------------------------------------------------------------------------
# detect_anomalies
# ---------------------------------------------------------------------------

def test_detect_invalid_expression_returns_error():
    result = detect_anomalies("not a cron")
    assert not result.ok
    assert result.error is not None


def test_detect_no_anomalies_for_normal_expression():
    result = detect_anomalies("0 9 * * 1-5")
    assert result.ok
    codes = [w.code for w in result.warnings]
    assert "IMPOSSIBLE_DATE" not in codes
    assert "LEAP_DAY_ONLY" not in codes


def test_detect_feb_31_is_impossible():
    result = detect_anomalies("0 0 31 2 *")
    assert result.ok  # syntactically valid
    codes = [w.code for w in result.warnings]
    assert "IMPOSSIBLE_DATE" in codes or "NO_NEXT_RUN" in codes


def test_detect_leap_day_only():
    result = detect_anomalies("0 0 29 2 *")
    assert result.ok
    codes = [w.code for w in result.warnings]
    assert "LEAP_DAY_ONLY" in codes


def test_detect_leap_day_critical_severity_absent_for_normal():
    result = detect_anomalies("30 6 * * *")
    critical = [w for w in result.warnings if w.severity == "critical"]
    assert critical == []


# ---------------------------------------------------------------------------
# format helpers
# ---------------------------------------------------------------------------

def test_format_anomaly_warning_contains_code():
    w = AnomalyWarning(code="FOO", message="bar", severity="warning")
    out = format_anomaly_warning(w)
    assert "FOO" in out
    assert "bar" in out


def test_format_anomaly_result_no_warnings():
    r = AnomalyResult(expression="0 * * * *")
    out = format_anomaly_result(r)
    assert "No anomalies" in out
    assert "0 * * * *" in out


def test_format_anomaly_result_with_error():
    r = AnomalyResult(expression="bad", error="parse error")
    out = format_anomaly_result(r)
    assert "ERROR" in out
    assert "parse error" in out


def test_format_anomaly_results_summary_line():
    r1 = AnomalyResult(expression="0 * * * *")
    r2 = AnomalyResult(expression="bad", error="oops")
    out = format_anomaly_results([r1, r2])
    assert "1/2" in out
