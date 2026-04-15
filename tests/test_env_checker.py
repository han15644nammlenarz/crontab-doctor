"""Tests for crontab_doctor.env_checker."""
import pytest

from crontab_doctor.env_checker import (
    EnvCheckResult,
    check_env,
    extract_env_vars,
)


def test_extract_no_vars():
    assert extract_env_vars("/usr/bin/backup.sh") == []


def test_extract_dollar_var():
    assert extract_env_vars("echo $HOME") == ["HOME"]


def test_extract_braced_var():
    assert extract_env_vars("echo ${MY_VAR}") == ["MY_VAR"]


def test_extract_multiple_vars():
    result = extract_env_vars("$FOO $BAR $FOO")
    # duplicates collapsed, order preserved
    assert result == ["FOO", "BAR"]


def test_check_env_no_command():
    result = check_env("* * * * *", command=None)
    assert result.ok
    assert result.referenced == []
    assert result.missing == []


def test_check_env_all_defined():
    env = {"HOME": "/root", "USER": "alice"}
    result = check_env("0 * * * *", command="echo $HOME $USER", environ=env)
    assert result.ok
    assert set(result.defined) == {"HOME", "USER"}
    assert result.missing == []


def test_check_env_some_missing():
    env = {"HOME": "/root"}
    result = check_env("0 * * * *", command="echo $HOME $MISSING_VAR", environ=env)
    assert not result.ok
    assert "MISSING_VAR" in result.missing
    assert "HOME" in result.defined


def test_check_env_all_missing():
    result = check_env("*/5 * * * *", command="$ALPHA $BETA", environ={})
    assert not result.ok
    assert set(result.missing) == {"ALPHA", "BETA"}
    assert result.defined == []


def test_summary_no_refs():
    result = check_env("* * * * *", command=None)
    assert "No environment variables" in result.summary()


def test_summary_with_defined_and_missing():
    env = {"A": "1"}
    result = check_env("0 0 * * *", command="$A $B", environ=env)
    s = result.summary()
    assert "A" in s
    assert "B" in s


def test_env_check_result_repr_ok_flag():
    r = EnvCheckResult(expression="* * * * *", command=None)
    assert r.ok is True
