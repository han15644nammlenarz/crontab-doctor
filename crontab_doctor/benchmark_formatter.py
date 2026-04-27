"""Formatter for BenchmarkResult output."""
from __future__ import annotations

import sys

from .cron_benchmark import BenchmarkResult

_COLORS = sys.stdout.isatty()


def _c(text: str, code: str) -> str:
    if not _COLORS:
        return text
    return f"\033[{code}m{text}\033[0m"


def _rank_color(rank: int) -> str:
    if rank == 1:
        return "33"   # yellow / gold
    if rank == 2:
        return "37"   # white / silver
    if rank == 3:
        return "31"   # red / bronze
    return "0"


def format_benchmark(result: BenchmarkResult) -> str:
    if not result.ok:
        return _c(f"✖ {result.error}", "31")

    if not result.entries:
        return _c("⚠ No expressions to benchmark.", "33")

    lines: list[str] = [
        _c(f"Benchmark — {len(result.entries)} expression(s)", "1"),
    ]
    for entry in result.entries:
        rank_str = _c(f"#{entry.rank}", _rank_color(entry.rank))
        label = f" {_c(entry.label, '36')}" if entry.label else ""
        expr = _c(entry.expression, "1")
        cat = _c(entry.result.category, "32")
        rpd = f"{entry.result.runs_per_day:.1f} runs/day"
        lines.append(f"  {rank_str} {expr}{label} — {cat} ({rpd})")

    return "\n".join(lines)
