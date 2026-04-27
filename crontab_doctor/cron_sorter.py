"""Sort and rank cron expressions by frequency, next run, or label."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse_expression, ParseError
from .next_run import next_runs, NextRunError
from .frequency_analyzer import analyze_frequency

VALID_KEYS = ("frequency", "next_run", "expression", "label")


@dataclass
class SortEntry:
    expression: str
    label: Optional[str] = None
    rank: int = 0
    sort_key: str = ""
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "label": self.label,
            "rank": self.rank,
            "sort_key": self.sort_key,
            "error": self.error,
        }


@dataclass
class SortResult:
    entries: List[SortEntry] = field(default_factory=list)
    sort_by: str = "frequency"
    error: Optional[str] = None

    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"Sort error: {self.error}"
        valid = [e for e in self.entries if e.error is None]
        invalid = [e for e in self.entries if e.error is not None]
        parts = [f"{len(valid)} expression(s) sorted by {self.sort_by}"]
        if invalid:
            parts.append(f"{len(invalid)} skipped due to errors")
        return "; ".join(parts)


def _key_for_frequency(expr: str) -> str:
    result = analyze_frequency(expr)
    if not result.ok():
        return "zzz"
    return result.category or "zzz"


def _key_for_next_run(expr: str) -> str:
    try:
        runs = next_runs(expr, count=1)
        if runs:
            return runs[0].isoformat()
    except (NextRunError, Exception):
        pass
    return "9999-99-99T99:99:99"


def sort_expressions(
    expressions: List[str],
    sort_by: str = "frequency",
    labels: Optional[List[Optional[str]]] = None,
    reverse: bool = False,
) -> SortResult:
    if sort_by not in VALID_KEYS:
        return SortResult(error=f"Invalid sort key '{sort_by}'. Choose from: {', '.join(VALID_KEYS)}")

    if labels is None:
        labels = [None] * len(expressions)
    elif len(labels) != len(expressions):
        return SortResult(error="Length of labels must match length of expressions")

    entries: List[SortEntry] = []
    for expr, lbl in zip(expressions, labels):
        entry = SortEntry(expression=expr, label=lbl)
        try:
            parse_expression(expr)
        except ParseError as exc:
            entry.error = str(exc)
            entries.append(entry)
            continue

        if sort_by == "frequency":
            entry.sort_key = _key_for_frequency(expr)
        elif sort_by == "next_run":
            entry.sort_key = _key_for_next_run(expr)
        elif sort_by == "expression":
            entry.sort_key = expr
        elif sort_by == "label":
            entry.sort_key = lbl or ""
        entries.append(entry)

    valid = sorted(
        [e for e in entries if e.error is None],
        key=lambda e: e.sort_key,
        reverse=reverse,
    )
    invalid = [e for e in entries if e.error is not None]
    ranked = valid + invalid
    for i, entry in enumerate(ranked):
        entry.rank = i + 1

    return SortResult(entries=ranked, sort_by=sort_by)
