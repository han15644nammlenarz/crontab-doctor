"""Tests for crontab_doctor.lint."""

import pytest

from crontab_doctor.lint import (
    LintWarning,
    lint_expression,
    _check_too_frequent,
    _check_midnight_congestion,
    _check_day_and_weekday_both_set,
    _check_large_step,
)
from crontab_doctor.parser import parse_expression


# ---------------------------------------------------------------------------
# LintWarning dataclass
# ---------------------------------------------------------------------------

def test_lint_warning_repr():
    w = LintWarning(code="L001", message="msg", severity="warning")
    assert "L001" in repr(w)
    assert "msg" in repr(w)


def test_lint_warning_default_severity():
    w = LintWarning(code="L001", message="msg")
    assert w.severity == "warning"


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def test_check_too_frequent_triggers_on_star_star():
    expr = parse_expression("* * * * *")
    warnings = _check_too_frequent(expr)
    assert any(w.code == "L001" for w in warnings)


def test_check_too_frequent_no_warning_for_specific_minute():
    expr = parse_expression("5 * * * *")
    warnings = _check_too_frequent(expr)
    assert warnings == []


def test_check_midnight_congestion_triggers():
    expr = parse_expression("0 0 * * *")
    warnings = _check_midnight_congestion(expr)
    assert any(w.code == "L002" for w in warnings)
    assert warnings[0].severity == "info"


def test_check_midnight_congestion_no_warning_for_other_times():
    expr = parse_expression("0 1 * * *")
    assert _check_midnight_congestion(expr) == []


def test_check_day_and_weekday_both_set():
    expr = parse_expression("0 12 15 * 1")
    warnings = _check_day_and_weekday_both_set(expr)
    assert any(w.code == "L003" for w in warnings)


def test_check_day_and_weekday_only_weekday():
    expr = parse_expression("0 12 * * 1")
    assert _check_day_and_weekday_both_set(expr) == []


def test_check_large_step_minute():
    expr = parse_expression("*/45 * * * *")
    warnings = _check_large_step(expr)
    assert any(w.code == "L004" for w in warnings)


def test_check_large_step_hour():
    expr = parse_expression("0 */13 * * *")
    warnings = _check_large_step(expr)
    assert any(w.code == "L004" for w in warnings)


def test_check_large_step_small_step_no_warning():
    expr = parse_expression("*/5 * * * *")
    assert _check_large_step(expr) == []


# ---------------------------------------------------------------------------
# lint_expression integration
# ---------------------------------------------------------------------------

def test_lint_expression_every_minute_returns_l001():
    warnings = lint_expression("* * * * *")
    codes = [w.code for w in warnings]
    assert "L001" in codes


def test_lint_expression_invalid_expression_returns_empty():
    # Parser will raise; linter should swallow and return []
    warnings = lint_expression("99 99 99 99 99")
    assert warnings == []


def test_lint_expression_clean_expression_no_warnings():
    warnings = lint_expression("30 9 * * 1-5")
    assert warnings == []


def test_lint_expression_midnight_returns_l002():
    warnings = lint_expression("0 0 * * *")
    codes = [w.code for w in warnings]
    assert "L002" in codes
