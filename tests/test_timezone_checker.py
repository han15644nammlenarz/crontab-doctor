"""Tests for timezone_checker and cli_timezone."""
from __future__ import annotations

import json
from argparse import Namespace
from unittest.mock import patch

import pytest

from crontab_doctor.timezone_checker import TzCheckResult, check_timezone
from crontab_doctor.cli_timezone import build_timezone_parser, cmd_timezone


# ---------------------------------------------------------------------------
# TzCheckResult helpers
# ---------------------------------------------------------------------------

def test_tz_check_result_ok_when_no_errors():
    r = TzCheckResult(expression="* * * * *", timezone="UTC", timezone_valid=True)
    assert r.ok is True


def test_tz_check_result_not_ok_when_errors():
    r = TzCheckResult(
        expression="bad", timezone=None, timezone_valid=True, errors=["oops"]
    )
    assert r.ok is False


def test_tz_check_result_not_ok_when_invalid_tz():
    r = TzCheckResult(expression="* * * * *", timezone="Fake/Zone", timezone_valid=False)
    assert r.ok is False


def test_summary_contains_expression():
    r = TzCheckResult(expression="0 9 * * 1", timezone="Europe/London", timezone_valid=True)
    assert "0 9 * * 1" in r.summary()


def test_summary_none_timezone_shows_system_local():
    r = TzCheckResult(expression="* * * * *", timezone=None, timezone_valid=True)
    assert "system local" in r.summary()


# ---------------------------------------------------------------------------
# check_timezone logic
# ---------------------------------------------------------------------------

def test_check_valid_expression_no_tz():
    r = check_timezone("*/5 * * * *")
    assert r.ok is True
    assert r.timezone is None


def test_check_invalid_expression_produces_error():
    r = check_timezone("99 99 99 99 99")
    assert not r.ok
    assert r.errors


def test_check_known_tz_is_valid():
    r = check_timezone("0 6 * * *", timezone="America/New_York")
    # May warn if db unavailable, but should not error on a real IANA name
    assert r.timezone == "America/New_York"
    # timezone_valid True unless db says otherwise
    if not r.errorsvalid is True


def test_check_unknown_tz_produces_error():
    with patch("crontab_doctor.timezone_checker._available_timezones",
               return_value=frozenset({"UTC", "America/New_York"})):
        r = check_timezone("0 6 * * *", timezone="Fake/Zone")
    assert r.timezone_valid is False
    assert any("Fake/Zone" in e for e in r.errors)


def test_check_utc_offset_style_warns():
    with patch("crontab_doctor.timezone_checker._available_timezones",
               return_value=frozenset({"UTC+5"})):
        r = check_timezone("0 6 * * *", timezone="UTC+("fixed offset" in w for w in r.warnings)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def test_build_timezone_parser_parser():
    p = build_timezone_parser()
    assert p is not None


def test_cmd_timezone_exits_zero_for_valid(capsys):
    args 12 * * *", timezone=None, json=False)
    code = cmd_timezone(args)
    assert code == 0


def test_cmd_timezone_exits_one_for_invalid(capsys):
    args = Namespace(expression="99 99 99 99 99", timezone=None, json=False)
    code = cmd_timezone(args)
    assert code == 1


def test_cmd_timezone_json_output(capsys):
    args = Namespace(expression="*/10 * * * *", timezone=None, json=True)
    cmd_timezone(args)
    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert "expression" in data
    assert "ok" in data
