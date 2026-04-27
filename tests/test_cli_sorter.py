"""Tests for crontab_doctor.cli_sorter."""
from __future__ import annotations

import argparse
import pytest
from crontab_doctor.cli_sorter import build_sorter_parser, cmd_sort


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "expressions": ["0 * * * *"],
        "sort_by": "expression",
        "labels": None,
        "reverse": False,
        "no_color": True,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_build_sorter_parser_registers_sort():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command")
    p = build_sorter_parser(sub)
    assert p is not None


def test_cmd_sort_valid_expression_returns_zero():
    args = _make_args(expressions=["0 * * * *", "0 0 * * *"])
    assert cmd_sort(args) == 0


def test_cmd_sort_invalid_sort_key_returns_one():
    args = _make_args(sort_by="bogus")
    # sort_expressions will return error; cmd_sort returns 1
    # We need to bypass argparse choices validation, so patch sort_by
    import crontab_doctor.cli_sorter as mod
    from crontab_doctor.cron_sorter import SortResult
    original = mod.sort_expressions
    mod.sort_expressions = lambda **kw: SortResult(error="bad key")
    try:
        result = cmd_sort(args)
        assert result == 1
    finally:
        mod.sort_expressions = original


def test_cmd_sort_with_labels_returns_zero():
    args = _make_args(
        expressions=["0 * * * *", "0 0 * * *"],
        labels=["a", "b"],
        sort_by="label",
    )
    assert cmd_sort(args) == 0


def test_cmd_sort_reverse_flag_returns_zero():
    args = _make_args(
        expressions=["5 * * * *", "0 * * * *"],
        sort_by="expression",
        reverse=True,
    )
    assert cmd_sort(args) == 0


def test_cmd_sort_invalid_expression_still_returns_zero():
    # Invalid expressions are demoted to end but result.ok() is still True
    args = _make_args(expressions=["not-valid", "0 * * * *"])
    assert cmd_sort(args) == 0


def test_cmd_sort_no_color_produces_output(capsys):
    args = _make_args(expressions=["0 * * * *"], no_color=True)
    cmd_sort(args)
    captured = capsys.readouterr()
    assert "0 * * * *" in captured.out
