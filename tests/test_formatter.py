"""Tests for crontab_doctor.formatter module."""

import pytest
from crontab_doctor.auditor import AuditResult
from crontab_doctor.conflict_detector import Conflict
from crontab_doctor.formatter import (
    format_audit_result,
    format_conflicts,
    format_summary,
)


def make_result(expression, explanation="", errors=None, warnings=None):
    return AuditResult(
        expression=expression,
        explanation=explanation,
        errors=errors or [],
        warnings=warnings or [],
    )


def test_format_valid_result_contains_expression():
    result = make_result("0 * * * *", explanation="Every hour at minute 0")
    output = format_audit_result(result, use_color=False)
    assert "0 * * * *" in output
    assert "Every hour at minute 0" in output
    assert "valid" in output


def test_format_result_with_errors():
    result = make_result("99 * * * *", errors=["Minute value 99 out of range"])
    output = format_audit_result(result, use_color=False)
    assert "ERROR" in output
    assert "Minute value 99 out of range" in output
    assert "valid" not in output


def test_format_result_with_warnings():
    result = make_result("0 * * * *", warnings=["Runs frequently"])
    output = format_audit_result(result, use_color=False)
    assert "WARNING" in output
    assert "Runs frequently" in output


def test_format_result_no_explanation():
    result = make_result("*/5 * * * *")
    output = format_audit_result(result, use_color=False)
    assert "Schedule" not in output


def test_format_no_conflicts():
    output = format_conflicts([], use_color=False)
    assert "No conflicts detected" in output


def test_format_single_conflict():
    conflict = Conflict(
        expression_a="0 * * * *",
        expression_b="0 */1 * * *",
        reason="Both fire at the same minute each hour",
    )
    output = format_conflicts([conflict], use_color=False)
    assert "Conflicts detected: 1" in output
    assert "0 * * * *" in output
    assert "0 */1 * * *" in output
    assert "Both fire at the same minute each hour" in output


def test_format_multiple_conflicts():
    conflicts = [
        Conflict("a", "b", "reason1"),
        Conflict("c", "d", "reason2"),
    ]
    output = format_conflicts(conflicts, use_color=False)
    assert "Conflicts detected: 2" in output
    assert "[1]" in output
    assert "[2]" in output


def test_format_summary_all_valid():
    results = [
        make_result("0 * * * *"),
        make_result("*/5 * * * *"),
    ]
    output = format_summary(results, use_color=False)
    assert "Total: 2" in output
    assert "Valid: 2" in output
    assert "Invalid: 0" in output


def test_format_summary_mixed():
    results = [
        make_result("0 * * * *"),
        make_result("bad", errors=["parse error"]),
        make_result("*/5 * * * *", warnings=["frequent"]),
    ]
    output = format_summary(results, use_color=False)
    assert "Total: 3" in output
    assert "Valid: 2" in output
    assert "Invalid: 1" in output
    assert "Warnings: 1" in output
