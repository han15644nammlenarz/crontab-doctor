"""Retry policy advisor: suggests retry/backoff settings based on cron frequency."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, parse_expression, ParseError
from .conflict_detector import _expand_field


@dataclass
class RetryAdvice:
    expression: str
    interval_minutes: Optional[int]  # None means non-uniform / complex
    suggestions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"Expression : {self.expression}"]
        if self.interval_minutes is not None:
            lines.append(f"Interval   : ~{self.interval_minutes} min")
        else:
            lines.append("Interval   : variable / complex schedule")
        for s in self.suggestions:
            lines.append(f"  [suggest] {s}")
        for w in self.warnings:
            lines.append(f"  [warn]    {w}")
        return "\n".join(lines)


def _estimate_interval(expr: CronExpression) -> Optional[int]:
    """Return approximate minutes between runs, or None if indeterminate."""
    minutes = _expand_field(expr.minute, 0, 59)
    hours = _expand_field(expr.hour, 0, 23)

    if len(minutes) == 60 and len(hours) == 24:
        return 1
    if len(minutes) == 60:
        return 1
    if len(hours) == 24 and len(minutes) == 1:
        return 60

    total_daily = len(hours) * len(minutes)
    if total_daily == 0:
        return None
    return max(1, 1440 // total_daily)


def advise_retry(expression: str) -> RetryAdvice:
    """Analyse a cron expression and return retry/backoff advice."""
    try:
        expr = parse_expression(expression)
    except ParseError as exc:
        return RetryAdvice(
            expression=expression,
            interval_minutes=None,
            warnings=[f"Cannot parse expression: {exc}"],
        )

    interval = _estimate_interval(expr)
    advice = RetryAdvice(expression=expression, interval_minutes=interval)

    if interval is not None and interval <= 5:
        advice.warnings.append(
            "Very frequent schedule — retries may overlap with the next run."
        )
        advice.suggestions.append(
            "Keep retry attempts ≤ 2 with a short backoff (e.g. 30 s)."
        )
    elif interval is not None and interval <= 60:
        advice.suggestions.append(
            f"Retry up to 3 times with exponential backoff capped at {interval // 2} min."
        )
    else:
        advice.suggestions.append(
            "Retry up to 5 times; exponential backoff is safe given the long interval."
        )

    minutes = _expand_field(expr.minute, 0, 59)
    if 0 in minutes and len(minutes) == 1:
        advice.suggestions.append(
            "Job runs exactly on the hour — add a small random jitter (1-3 min) "
            "to avoid thundering-herd if many jobs share this schedule."
        )

    return advice
