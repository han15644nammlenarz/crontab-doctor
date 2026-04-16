"""Generate a calendar view of upcoming cron run times."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
from .next_run import next_runs, NextRunError


@dataclass
class CalendarEntry:
    expression: str
    label: Optional[str]
    runs: List[datetime]

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "label": self.label,
            "runs": [dt.isoformat() for dt in self.runs],
        }


@dataclass
class CalendarResult:
    entries: List[CalendarEntry] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if not self.ok:
            return f"Calendar error: {self.error}"
        total = sum(len(e.runs) for e in self.entries)
        return f"{len(self.entries)} expression(s), {total} upcoming run(s) shown."


def build_calendar(
    expressions: List[str],
    labels: Optional[List[Optional[str]]] = None,
    since: Optional[datetime] = None,
    count: int = 5,
    window_hours: int = 24,
) -> CalendarResult:
    """Build a calendar of upcoming runs for each expression."""
    if since is None:
        since = datetime.now().replace(second=0, microsecond=0)
    until = since + timedelta(hours=window_hours)
    resolved_labels: List[Optional[str]] = labels if labels else [None] * len(expressions)
    if len(resolved_labels) < len(expressions):
        resolved_labels += [None] * (len(expressions) - len(resolved_labels))

    entries: List[CalendarEntry] = []
    for expr, lbl in zip(expressions, resolved_labels):
        try:
            runs = next_runs(expr, since=since, n=count)
            runs = [r for r in runs if r <= until]
        except NextRunError as exc:
            return CalendarResult(error=str(exc))
        entries.append(CalendarEntry(expression=expr, label=lbl, runs=runs))

    return CalendarResult(entries=entries)
