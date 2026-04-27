"""Tests for cron_validator_report module."""
import pytest
from crontab_doctor.cron_validator_report import (
    ExpressionReport,
    ValidationReport,
    build_validation_report,
)


# ---------------------------------------------------------------------------
# ExpressionReport
# ---------------------------------------------------------------------------

def _make_report(expr="* * * * *", parse_error=None, val_errors=None, lint_warnings=None):
    return ExpressionReport(
        expression=expr,
        command=None,
        parse_error=parse_error,
        validation_errors=val_errors or [],
        lint_warnings=lint_warnings or [],
    )


def test_expression_report_ok_when_no_errors():
    r = _make_report()
    assert r.ok is True


def test_expression_report_not_ok_when_parse_error():
    r = _make_report(parse_error="unexpected token")
    assert r.ok is False


def test_expression_report_not_ok_when_validation_errors():
    r = _make_report(val_errors=["minute out of range"])
    assert r.ok is False


def test_expression_report_summary_ok_no_warnings():
    r = _make_report(expr="0 * * * *")
    assert "[OK]" in r.summary()
    assert "0 * * * *" in r.summary()


def test_expression_report_summary_ok_with_warnings():
    r = _make_report(expr="* * * * *", lint_warnings=["too frequent"])
    s = r.summary()
    assert "[OK]" in s
    assert "1 lint warning" in s


def test_expression_report_summary_parse_error():
    r = _make_report(expr="bad expr", parse_error="unexpected token")
    s = r.summary()
    assert "[INVALID]" in s
    assert "unexpected token" in s


def test_expression_report_summary_validation_error():
    r = _make_report(expr="99 * * * *", val_errors=["minute out of range"])
    s = r.summary()
    assert "[INVALID]" in s
    assert "minute out of range" in s


# ---------------------------------------------------------------------------
# ValidationReport
# ---------------------------------------------------------------------------

def test_validation_report_ok_all_valid():
    r = ValidationReport(reports=[_make_report(), _make_report()])
    assert r.ok is True


def test_validation_report_not_ok_when_error_field_set():
    r = ValidationReport(error="something went wrong")
    assert r.ok is False


def test_validation_report_counts():
    r = ValidationReport(reports=[
        _make_report(),
        _make_report(parse_error="bad"),
        _make_report(val_errors=["oops"]),
    ])
    assert r.total == 3
    assert r.valid_count == 1
    assert r.invalid_count == 2


def test_validation_report_summary_contains_counts():
    r = ValidationReport(reports=[_make_report(), _make_report(parse_error="bad")])
    s = r.summary()
    assert "2 expression" in s
    assert "1 valid" in s
    assert "1 invalid" in s


def test_validation_report_summary_error():
    r = ValidationReport(error="No expressions provided.")
    assert "Error" in r.summary()


# ---------------------------------------------------------------------------
# build_validation_report integration
# ---------------------------------------------------------------------------

def test_build_report_empty_list_returns_error():
    r = build_validation_report([])
    assert r.error is not None
    assert not r.ok


def test_build_report_valid_expression():
    r = build_validation_report(["0 12 * * *"])
    assert r.total == 1
    assert r.valid_count == 1
    assert r.ok


def test_build_report_invalid_expression():
    r = build_validation_report(["99 99 99 99 99"])
    assert r.total == 1
    assert r.invalid_count == 1
    assert not r.ok


def test_build_report_mixed_expressions():
    r = build_validation_report(["0 * * * *", "not-a-cron"])
    assert r.total == 2
    assert r.valid_count == 1
    assert r.invalid_count == 1


def test_build_report_strips_whitespace():
    r = build_validation_report(["  0 6 * * 1  "])
    assert r.total == 1
    assert r.valid_count == 1
