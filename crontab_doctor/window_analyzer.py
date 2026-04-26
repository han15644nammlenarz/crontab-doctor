"""Analyze whether a cron expression fires within a given time window."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .next_run import NextRunError, next_runs


@dataclass
class WindowResult:
    expression: str
    window_start: datetime
    window_end: datetime
    fires: List[datetime] = field(default_factory=list)
    error: Optional[str] = None

    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        count = len(self.fires)
        noun = "time" if count == 1 else "times"
        span_minutes = int((self.window_end - self.window_start).total_seconds() / 60)
        return (
            f"'{self.expression}' fires {count} {noun} "
            f"in the next {span_minutes} minutes"
        )

    def next_fire(self) -> Optional[datetime]:
        """Return the earliest firing time within the window, or None if there are none."""
        return self.fires[0] if self.fires else None


def analyze_window(
    expression: str,
    window_minutes: int = 60,
    from_dt: Optional[datetime] = None,
) -> WindowResult:
    """Return all firing times for *expression* within *window_minutes* from *from_dt*.

    Args:
        expression: A cron expression string (e.g. ``"*/5 * * * *"``).
        window_minutes: Length of the look-ahead window in minutes.  Defaults to 60.
        from_dt: Start of the window.  Defaults to the current minute (seconds and
            microseconds zeroed out).

    Returns:
        A :class:`WindowResult` containing every scheduled firing time that falls
        within ``[from_dt, from_dt + window_minutes)``.
    """
    if from_dt is None:
        from_dt = datetime.now().replace(second=0, microsecond=0)

    window_end = from_dt + timedelta(minutes=window_minutes)

    # Request enough candidates to cover a dense schedule (every minute = window_minutes hits)
    max_count = max(window_minutes, 5)

    try:
        candidates = next_runs(expression, count=max_count, from_dt=from_dt)
    except NextRunError as exc:
        return WindowResult(
            expression=expression,
            window_start=from_dt,
            window_end=window_end,
            error=str(exc),
        )

    fires = [dt for dt in candidates if from_dt <= dt < window_end]

    return WindowResult(
        expression=expression,
        window_start=from_dt,
        window_end=window_end,
        fires=fires,
    )
