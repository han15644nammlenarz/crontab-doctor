"""Tests for parser, validator, and explainer modules."""

import pytest
from crontab_doctor.parser import parse_expression, ParseError
from crontab_doctor.validator import validate_expression
from crontab_doctor.explainer import explain


# --- Parser tests ---

def test_parse_basic_expression():
    expr = parse_expression("0 12 * * 1")
    assert len(expr.fields) == 5
    assert expr.fields[0].raw == "0"
    assert expr.fields[1].raw == "12"
    assert expr.command is None


def test_parse_with_command():
    expr = parse_expression("30 6 * * * /usr/bin/backup.sh")
    assert expr.command == "/usr/bin/backup.sh"


def test_parse_special_at_daily():
    expr = parse_expression("@daily")
    assert expr.fields[0].raw == "0"  # minute
    assert expr.fields[1].raw == "0"  # hour


def test_parse_special_at_hourly():
    expr = parse_expression("@hourly")
    assert expr.fields[0].raw == "0"
    assert expr.fields[1].raw == "*"


def test_parse_month_alias():
    expr = parse_expression("0 0 1 Jan *")
    assert expr.fields[3].raw == "1"


def test_parse_dow_alias():
    expr = parse_expression("0 0 * * Mon")
    assert expr.fields[4].raw == "1"


def test_parse_too_few_fields():
    with pytest.raises(ParseError):
        parse_expression("0 12 *")


# --- Validator tests ---

def test_valid_expression_no_errors():
    expr = parse_expression("*/15 0-23 1,15 * 1-5")
    errors = validate_expression(expr)
    assert errors == []


def test_invalid_minute_out_of_range():
    expr = parse_expression("60 12 * * *")
    errors = validate_expression(expr)
    assert any(e.field == "minute" for e in errors)


def test_invalid_hour_out_of_range():
    expr = parse_expression("0 25 * * *")
    errors = validate_expression(expr)
    assert any(e.field == "hour" for e in errors)


def test_invalid_range_low_greater_than_high():
    expr = parse_expression("0 12 20-10 * *")
    errors = validate_expression(expr)
    assert any("greater than" in e.message for e in errors)


def test_step_zero_is_invalid():
    expr = parse_expression("*/0 * * * *")
    errors = validate_expression(expr)
    assert any("zero" in e.message for e in errors)


# --- Explainer tests ---

def test_explain_every_minute():
    expr = parse_expression("* * * * *")
    result = explain(expr)
    assert "every minute" in result.lower()


def test_explain_specific_time():
    expr = parse_expression("0 9 * * *")
    result = explain(expr)
    assert "9" in result


def test_explain_with_dow():
    expr = parse_expression("0 8 * * 1")
    result = explain(expr)
    assert "monday" in result.lower()


def test_explain_with_month():
    expr = parse_expression("0 0 1 6 *")
    result = explain(expr)
    assert "june" in result.lower()
