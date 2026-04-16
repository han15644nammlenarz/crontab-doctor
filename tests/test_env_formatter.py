"""Tests for crontab_doctor.env_formatter."""
import pytest

from crontab_doctor.env_checker import EnvCheckResult
from crontab_doctor.env_formatter import format_env_result, format_env_results


def _result(expr="* * * * *", command=None, referenced=None,
            defined=None, missing=None) -> EnvCheckResult:
    r = EnvCheckResult(
        expression=expr,
        command=command,
        referenced=referenced or [],
        defined=defined or [],
        missing=missing or [],
    )
    return r


def test_format_contains_expression():
    r = _result(expr="0 * * * *")
    out = format_env_result(r, color=False)
    assert "0 * * * *" in out


def test_format_no_vars_message():
    r = _result()
    out = format_env_result(r, color=False)
    assert "No environment variables referenced" in out


def test_format_shows_defined_var():
    r = _result(
        command="echo $HOME",
        referenced=["HOME"],
        defined=["HOME"],
        missing=[],
    )
    out = format_env_result(r, color=False)
    assert "HOME" in out
    assert "defined" in out


def test_format_shows_missing_var():
    r = _result(
        command="echo $GHOST",
        referenced=["GHOST"],
        defined=[],
        missing=["GHOST"],
    )
    out = format_env_result(r, color=False)
    assert "GHOST" in out
    assert "MISSING" in out


def test_format_warning_line_when_missing():
    r = _result(
        command="$X",
        referenced=["X"],
        defined=[],
        missing=["X"],
    )
    out = format_env_result(r, color=False)
    assert "WARNING" in out


def test_format_ok_line_when_all_defined():
    r = _result(
        command="$Y",
        referenced=["Y"],
        defined=["Y"],
        missing=[],
    )
    out = format_env_result(r, color=False)
    assert "All environment variables are defined" in out


def test_format_multiple_results_separator():
    r1 = _result(expr="* * * * *")
    r2 = _result(expr="0 0 * * *")
    out = format_env_results([r1, r2], color=False)
    assert "* * * * *" in out
    assert "0 0 * * *" in out
    assert "-" * 10 in out


def test_format_color_disabled_no_escape_codes():
    r = _result(
        command="$MISSING",
        referenced=["MISSING"],
        defined=[],
        missing=["MISSING"],
    )
    out = format_env_result(r, color=False)
    assert "\033[" not in out


def test_format_shows_command():
    """The formatted output should include the cron command when present."""
    r = _result(
        expr="30 6 * * *",
        command="/usr/bin/backup.sh",
        referenced=[],
        defined=[],
        missing=[],
    )
    out = format_env_result(r, color=False)
    assert "/usr/bin/backup.sh" in out
