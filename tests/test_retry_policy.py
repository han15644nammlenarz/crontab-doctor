"""Tests for crontab_doctor.retry_policy and crontab_doctor.cli_retry."""

import json
import pytest
from unittest.mock import patch

from crontab_doctor.retry_policy import advise_retry, _estimate_interval
from crontab_doctor.parser import parse_expression
from crontab_doctor.cli_retry import build_retry_parser, cmd_retry


# ---------------------------------------------------------------------------
# _estimate_interval
# ---------------------------------------------------------------------------

def test_estimate_every_minute():
    expr = parse_expression("* * * * *")
    assert _estimate_interval(expr) == 1


def test_estimate_every_five_minutes():
    expr = parse_expression("*/5 * * * *")
    assert _estimate_interval(expr) == 1  # 12 * 24 runs/day → 5 min


def test_estimate_hourly():
    expr = parse_expression("0 * * * *")
    assert _estimate_interval(expr) == 60


def test_estimate_daily():
    expr = parse_expression("0 9 * * *")
    assert _estimate_interval(expr) == 1440


# ---------------------------------------------------------------------------
# advise_retry — suggestions & warnings
# ---------------------------------------------------------------------------

def test_advise_very_frequent_has_warning():
    advice = advise_retry("* * * * *")
    assert advice.interval_minutes == 1
    assert any("overlap" in w for w in advice.warnings)


def test_advise_very_frequent_short_retry_suggestion():
    advice = advise_retry("*/5 * * * *")
    assert any("2" in s for s in advice.suggestions)


def test_advise_hourly_suggests_three_retries():
    advice = advise_retry("0 * * * *")
    assert any("3" in s for s in advice.suggestions)
    assert advice.warnings == []


def test_advise_daily_suggests_five_retries():
    advice = advise_retry("0 9 * * *")
    assert any("5" in s for s in advice.suggestions)


def test_advise_on_the_hour_suggests_jitter():
    advice = advise_retry("0 6 * * *")
    assert any("jitter" in s for s in advice.suggestions)


def test_advise_invalid_expression_returns_warning():
    advice = advise_retry("not a cron")
    assert advice.interval_minutes is None
    assert advice.warnings
    assert "Cannot parse" in advice.warnings[0]


def test_advice_summary_contains_expression():
    advice = advise_retry("0 12 * * *")
    summary = advice.summary()
    assert "0 12 * * *" in summary


def test_advice_summary_contains_interval():
    advice = advise_retry("0 12 * * *")
    assert "1440" in advice.summary()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _run(args_list):
    parser = build_retry_parser()
    args = parser.parse_args(args_list)
    return cmd_retry(args)


def test_cli_valid_expression_exits_zero(capsys):
    rc = _run(["0 9 * * *"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Expression" in out


def test_cli_frequent_expression_exits_one(capsys):
    rc = _run(["* * * * *"])
    assert rc == 1


def test_cli_json_output(capsys):
    _run(["--json", "0 9 * * *"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "expression" in data
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)


def test_cli_json_invalid_expression(capsys):
    rc = _run(["--json", "bad expr"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["warnings"]
    assert rc == 1
