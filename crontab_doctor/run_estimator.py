"""Estimates how many times a cron expression will run in a given time window."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .next_run import next_runs, NextRunError
from .parser import parse_expression, ParseError


@dataclass
class RunEstimate:
    expression: str
    window_hours: int
    count: int
    first_run: Optional[datetime]
    last_run: Optional[datetime]
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        noun = "time" if self.count == 1 else "times"
        window = f"{self.window_hours}h window"
        if self.count == 0:
            return f"Never runs in a {window}."
        first = self.first_run.strftime("%Y-%m-%d %H:%M") if self.first_run else "N/A"
        last = self.last_run.strftime("%Y-%m-%d %H:%M") if self.last_run else "N/A"
        return (
            f"Runs {self.count} {noun} in a {window}. "
            f"First: {first}, Last: {last}."
        )


def estimate_runs(
    expression: str,
    window_hours: int = 24,
    from_dt: Optional[datetime] = None,
) -> RunEstimate:
    """Count how many times *expression* fires within *window_hours* from *from_dt*."""
    if window_hours <= 0:
        return RunEstimate(
            expression=expression,
            window_hours=window_hours,
            count=0,
            first_run=None,
            last_run=None,
            error="window_hours must be a positive integer",
        )

    try:
        parse_expression(expression)
    except ParseError as exc:
        return RunEstimate(
            expression=expression,
            window_hours=window_hours,
            count=0,
            first_run=None,
            last_run=None,
            error=str(exc),
        )

    base = from_dt or datetime.now().replace(second=0, microsecond=0)
    deadline = base + timedelta(hours=window_hours)

    # Request enough candidate runs to cover the window; cap at a safe limit.
    max_candidates = min(window_hours * 60 + 1, 10_000)

    try:
        candidates = next_runs(expression, n=max_candidates, from_dt=base)
    except NextRunError as exc:
        return RunEstimate(
            expression=expression,
            window_hours=window_hours,
            count=0,
            first_run=None,
            last_run=None,
            error=str(exc),
        )

    in_window = [dt for dt in candidates if base <= dt < deadline]

    warnings: List[str] = []
    if len(candidates) == max_candidates and (not in_window or candidates[-1] < deadline):
        warnings.append("Result may be truncated; window is very large.")

    return RunEstimate(
        expression=expression,
        window_hours=window_hours,
        count=len(in_window),
        first_run=in_window[0] if in_window else None,
        last_run=in_window[-1] if in_window else None,
        warnings=warnings,
    )
