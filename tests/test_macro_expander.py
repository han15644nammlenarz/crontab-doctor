"""Tests for macro_expander and cli_macro."""

import pytest
from unittest.mock import patch

from crontab_doctor.macro_expander import (
    expand_macro,
    list_macros,
    BUILTIN_MACROS,
    MacroExpansion,
)
from crontab_doctor.cli_macro import build_macro_parser, cmd_macro


def test_list_macros_returns_sorted():
    macros = list_macros()
    assert macros == sorted(macros)
    assert len(macros) > 0


def test_list_macros_contains_common_names():
    macros = list_macros()
    for name in ("daily", "hourly", "weekly", "monthly"):
        assert name in macros


def test_expand_known_macro_ok():
    result = expand_macro("daily")
    assert result.ok
    assert result.expanded == "0 0 * * *"
    assert result.name == "daily"


def test_expand_every_minute():
    result = expand_macro("every_minute")
    assert result.ok
    assert result.expanded == "* * * * *"


def test_expand_unknown_macro_not_ok():
    result = expand_macro("nonexistent_macro")
    assert not result.ok
    assert "nonexistent_macro" in result.error
    assert result.expanded == ""


def test_macro_expansion_summary_ok():
    result = expand_macro("hourly")
    summary = result.summary()
    assert "hourly" in summary
    assert "0 * * * *" in summary


def test_macro_expansion_summary_error():
    result = expand_macro("bad")
    summary = result.summary()
    assert "ERROR" in summary
    assert "bad" in summary


def test_macro_expansion_has_description():
    result = expand_macro("daily")
    assert result.description != ""
    assert "midnight" in result.description.lower()


def test_all_builtins_expand_successfully():
    for name in BUILTIN_MACROS:
        result = expand_macro(name)
        assert result.ok, f"Macro '{name}' failed to expand"
        assert result.expanded


def _run_cmd(argv):
    parser = build_macro_parser()
    args = parser.parse_args(argv)
    return cmd_macro(args)


def test_cmd_expand_known_exits_zero(capsys):
    rc = _run_cmd(["expand", "weekly"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "0 0 * * 0" in out


def test_cmd_expand_unknown_exits_one(capsys):
    rc = _run_cmd(["expand", "nope"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "ERROR" in out


def test_cmd_list_exits_zero(capsys):
    rc = _run_cmd(["list"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "daily" in out
    assert "hourly" in out
