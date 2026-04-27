"""Tests for cron_benchmark, benchmark_formatter, and cli_benchmark."""
from __future__ import annotations

from unittest.mock import patch
import argparse
import pytest

from crontab_doctor.cron_benchmark import (
    BenchmarkEntry,
    BenchmarkResult,
    benchmark_expressions,
)
from crontab_doctor.benchmark_formatter import format_benchmark
from crontab_doctor.cli_benchmark import build_benchmark_parser, cmd_benchmark
from crontab_doctor.frequency_analyzer import FrequencyResult


# ---------------------------------------------------------------------------
# BenchmarkResult helpers
# ---------------------------------------------------------------------------

def _freq(category: str, rpd: float) -> FrequencyResult:
    return FrequencyResult(category=category, runs_per_day=rpd)


def test_benchmark_result_ok_when_no_error():
    r = BenchmarkResult()
    assert r.ok is True


def test_benchmark_result_not_ok_when_error():
    r = BenchmarkResult(error="oops")
    assert r.ok is False


def test_benchmark_result_summary_error():
    r = BenchmarkResult(error="oops")
    assert "oops" in r.summary()


def test_benchmark_result_summary_empty():
    r = BenchmarkResult(entries=[])
    assert "No expressions" in r.summary()


def test_benchmark_result_summary_lists_ranks():
    e1 = BenchmarkEntry(expression="* * * * *", label=None, result=_freq("every-minute", 1440), rank=1)
    e2 = BenchmarkEntry(expression="0 * * * *", label=None, result=_freq("hourly", 24), rank=2)
    r = BenchmarkResult(entries=[e1, e2])
    s = r.summary()
    assert "#1" in s
    assert "#2" in s


# ---------------------------------------------------------------------------
# benchmark_expressions
# ---------------------------------------------------------------------------

def test_benchmark_no_expressions_returns_error():
    r = benchmark_expressions([])
    assert not r.ok
    assert "No expressions" in r.error  # type: ignore[arg-type]


def test_benchmark_label_length_mismatch_returns_error():
    r = benchmark_expressions(["* * * * *"], labels=["a", "b"])
    assert not r.ok


def test_benchmark_single_expression_rank_one():
    r = benchmark_expressions(["0 0 * * *"])
    assert r.ok
    assert len(r.entries) == 1
    assert r.entries[0].rank == 1


def test_benchmark_ranks_descending_by_frequency():
    r = benchmark_expressions(["0 0 * * *", "* * * * *"])
    assert r.ok
    assert r.entries[0].expression == "* * * * *"
    assert r.entries[0].rank == 1
    assert r.entries[1].expression == "0 0 * * *"
    assert r.entries[1].rank == 2


def test_benchmark_labels_attached():
    r = benchmark_expressions(["0 0 * * *"], labels=["nightly"])
    assert r.ok
    assert r.entries[0].label == "nightly"


def test_benchmark_entry_to_dict():
    e = BenchmarkEntry(expression="* * * * *", label="all", result=_freq("every-minute", 1440), rank=1)
    d = e.to_dict()
    assert d["expression"] == "* * * * *"
    assert d["label"] == "all"
    assert d["rank"] == 1
    assert d["runs_per_day"] == 1440


# ---------------------------------------------------------------------------
# format_benchmark
# ---------------------------------------------------------------------------

def test_format_benchmark_error():
    r = BenchmarkResult(error="bad input")
    out = format_benchmark(r)
    assert "bad input" in out


def test_format_benchmark_no_entries():
    r = BenchmarkResult(entries=[])
    out = format_benchmark(r)
    assert "No expressions" in out


def test_format_benchmark_contains_rank():
    r = benchmark_expressions(["0 0 * * *", "* * * * *"])
    out = format_benchmark(r)
    assert "#1" in out
    assert "#2" in out


def test_format_benchmark_contains_expression():
    r = benchmark_expressions(["0 0 * * *"])
    out = format_benchmark(r)
    assert "0 0 * * *" in out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def test_build_benchmark_parser_accepts_expressions():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command")
    build_benchmark_parser(sub)
    args = root.parse_args(["benchmark", "* * * * *", "0 0 * * *"])
    assert args.expressions == ["* * * * *", "0 0 * * *"]


def test_cmd_benchmark_exits_zero_on_valid(capsys):
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command")
    build_benchmark_parser(sub)
    args = root.parse_args(["benchmark", "* * * * *"])
    code = cmd_benchmark(args)
    assert code == 0


def test_cmd_benchmark_exits_one_on_error(capsys):
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command")
    build_benchmark_parser(sub)
    args = root.parse_args(["benchmark", "* * * * *"])
    args.expressions = []  # force error
    code = cmd_benchmark(args)
    assert code == 1
