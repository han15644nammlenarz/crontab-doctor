"""Tests for crontab_doctor.cron_normalizer."""
import pytest
from crontab_doctor.cron_normalizer import normalize_expression, NormalizeResult


# ---------------------------------------------------------------------------
# NormalizeResult helpers
# ---------------------------------------------------------------------------

def test_result_ok_when_no_error():
    r = NormalizeResult(original="* * * * *", normalized="* * * * *", changed=False)
    assert r.ok() is True


def test_result_not_ok_when_error():
    r = NormalizeResult(original="bad", normalized=None, changed=False, error="oops")
    assert r.ok() is False


def test_summary_unchanged():
    r = NormalizeResult(original="* * * * *", normalized="* * * * *", changed=False)
    assert "canonical" in r.summary().lower()


def test_summary_changed():
    r = NormalizeResult(original="0 0 1 jan *", normalized="0 0 1 1 *", changed=True)
    assert "->" in r.summary()


def test_summary_error():
    r = NormalizeResult(original="bad", normalized=None, changed=False, error="too short")
    assert "error" in r.summary().lower()


# ---------------------------------------------------------------------------
# Special @aliases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("alias,expected", [
    ("@daily",    "0 0 * * *"),
    ("@midnight", "0 0 * * *"),
    ("@hourly",   "0 * * * *"),
    ("@weekly",   "0 0 * * 0"),
    ("@monthly",  "0 0 1 * *"),
    ("@yearly",   "0 0 1 1 *"),
    ("@annually", "0 0 1 1 *"),
])
def test_special_aliases_expand(alias, expected):
    result = normalize_expression(alias)
    assert result.ok()
    assert result.normalized == expected
    assert result.changed is True


def test_special_alias_case_insensitive():
    result = normalize_expression("@Daily")
    assert result.ok()
    assert result.normalized == "0 0 * * *"


# ---------------------------------------------------------------------------
# Month name replacement
# ---------------------------------------------------------------------------

def test_month_name_jan_replaced():
    result = normalize_expression("0 0 1 jan *")
    assert result.ok()
    assert result.normalized == "0 0 1 1 *"
    assert result.changed is True


def test_month_name_dec_replaced():
    result = normalize_expression("0 12 * dec *")
    assert result.ok()
    assert "12" in result.normalized


# ---------------------------------------------------------------------------
# Weekday name replacement
# ---------------------------------------------------------------------------

def test_weekday_mon_replaced():
    result = normalize_expression("0 9 * * mon")
    assert result.ok()
    assert result.normalized == "0 9 * * 1"
    assert result.changed is True


def test_weekday_fri_replaced():
    result = normalize_expression("30 17 * * fri")
    assert result.ok()
    assert result.normalized == "30 17 * * 5"


# ---------------------------------------------------------------------------
# Already canonical expressions
# ---------------------------------------------------------------------------

def test_already_canonical_not_changed():
    result = normalize_expression("*/5 * * * *")
    assert result.ok()
    assert result.changed is False
    assert result.normalized == "*/5 * * * *"


def test_with_command_fields_only_first_five_normalized():
    result = normalize_expression("0 0 1 jan * /usr/bin/backup")
    assert result.ok()
    assert result.normalized == "0 0 1 1 *"


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_too_few_fields_returns_error():
    result = normalize_expression("* * *")
    assert not result.ok()
    assert result.normalized is None
    assert "5" in result.error


def test_invalid_value_returns_error():
    result = normalize_expression("99 * * * *")
    assert not result.ok()
    assert result.normalized is None
