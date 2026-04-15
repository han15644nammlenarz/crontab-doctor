"""Tests for crontab_doctor.lint_formatter."""

import pytest

from crontab_doctor.lint import LintWarning
from crontab_doctor.lint_formatter import (
    format_lint_warning,
    format_lint_results,
    format_lint_summary,
)


def _warn(code="L001", message="test msg", severity="warning"):
    return LintWarning(code=code, message=message, severity=severity)


# ---------------------------------------------------------------------------
# format_lint_warning
# ---------------------------------------------------------------------------

def test_format_lint_warning_contains_code():
    w = _warn(code="L001")
    result = format_lint_warning(w, color=False)
    assert "L001" in result


def test_format_lint_warning_contains_message():
    w = _warn(message="something suspicious")
    result = format_lint_warning(w, color=False)
    assert "something suspicious" in result


def test_format_lint_warning_info_severity_prefix():
    w = _warn(severity="info")
    result = format_lint_warning(w, color=False)
    assert "ℹ" in result


def test_format_lint_warning_warning_severity_prefix():
    w = _warn(severity="warning")
    result = format_lint_warning(w, color=False)
    assert "⚠" in result


# ---------------------------------------------------------------------------
# format_lint_results
# ---------------------------------------------------------------------------

def test_format_lint_results_no_warnings_shows_ok():
    output = format_lint_results("30 9 * * 1-5", [], color=False)
    assert "No lint warnings" in output


def test_format_lint_results_contains_expression():
    output = format_lint_results("* * * * *", [], color=False)
    assert "* * * * *" in output


def test_format_lint_results_shows_warning_code():
    warnings = [_warn(code="L001", message="runs every minute")]
    output = format_lint_results("* * * * *", warnings, color=False)
    assert "L001" in output
    assert "runs every minute" in output


def test_format_lint_results_multiple_warnings():
    warnings = [
        _warn(code="L001", message="first"),
        _warn(code="L002", message="second", severity="info"),
    ]
    output = format_lint_results("0 0 * * *", warnings, color=False)
    assert "L001" in output
    assert "L002" in output


# ---------------------------------------------------------------------------
# format_lint_summary
# ---------------------------------------------------------------------------

def test_format_lint_summary_counts_expressions():
    results = {
        "* * * * *": [_warn()],
        "0 0 * * *": [],
    }
    output = format_lint_summary(results, color=False)
    assert "2" in output  # 2 expressions


def test_format_lint_summary_counts_total_warnings():
    results = {
        "* * * * *": [_warn(), _warn(code="L002")],
        "0 0 * * *": [_warn(code="L003")],
    }
    output = format_lint_summary(results, color=False)
    assert "3" in output  # 3 total warnings


def test_format_lint_summary_zero_warnings():
    results = {"30 9 * * 1-5": []}
    output = format_lint_summary(results, color=False)
    assert "0" in output
