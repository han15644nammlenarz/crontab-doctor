"""Benchmark cron expressions by comparing their run frequencies."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .frequency_analyzer import analyze_frequency, FrequencyResult


@dataclass
class BenchmarkEntry:
    expression: str
    label: Optional[str]
    result: FrequencyResult
    rank: int = 0

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "label": self.label,
            "category": self.result.category,
            "runs_per_day": self.result.runs_per_day,
            "rank": self.rank,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"BenchmarkEntry(expression={self.expression!r}, "
            f"rank={self.rank}, runs_per_day={self.result.runs_per_day})"
        )


@dataclass
class BenchmarkResult:
    entries: List[BenchmarkEntry] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"Benchmark error: {self.error}"
        if not self.entries:
            return "No expressions to benchmark."
        lines = [f"Benchmark — {len(self.entries)} expression(s) ranked by frequency:"]
        for e in self.entries:
            label = f" ({e.label})" if e.label else ""
            lines.append(
                f"  #{e.rank} {e.expression}{label} "
                f"— {e.result.category} ({e.result.runs_per_day:.1f} runs/day)"
            )
        return "\n".join(lines)


def benchmark_expressions(
    expressions: List[str],
    labels: Optional[List[Optional[str]]] = None,
) -> BenchmarkResult:
    """Rank *expressions* by descending run frequency."""
    if not expressions:
        return BenchmarkResult(error="No expressions provided.")

    resolved_labels: List[Optional[str]] = labels if labels else [None] * len(expressions)
    if len(resolved_labels) != len(expressions):
        return BenchmarkResult(error="Length of labels must match length of expressions.")

    entries: List[BenchmarkEntry] = []
    for expr, lbl in zip(expressions, resolved_labels):
        freq = analyze_frequency(expr)
        entries.append(BenchmarkEntry(expression=expr, label=lbl, result=freq))

    entries.sort(key=lambda e: e.result.runs_per_day, reverse=True)
    for rank, entry in enumerate(entries, start=1):
        entry.rank = rank

    return BenchmarkResult(entries=entries)
