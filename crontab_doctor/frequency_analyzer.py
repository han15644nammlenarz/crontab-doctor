"""Analyze and compare the execution frequency of cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse_expression, ParseError
from .run_estimator import estimate_runs


@dataclass
class FrequencyResult:
    expression: str
    runs_per_day: Optional[float]
    runs_per_week: Optional[float]
    runs_per_month: Optional[float]
    category: str  # 'very_high', 'high', 'medium', 'low', 'very_low'
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"FrequencyResult(error={self.error!r})"
        return (
            f"FrequencyResult(expression={self.expression!r}, "
            f"runs_per_day={self.runs_per_day:.1f}, category={self.category!r})"
        )


def _categorize(runs_per_day: float) -> str:
    if runs_per_day >= 60 * 24:  # every minute
        return "very_high"
    if runs_per_day >= 24:       # at least hourly
        return "high"
    if runs_per_day >= 1:        # at least daily
        return "medium"
    if runs_per_day >= 1 / 7:    # at least weekly
        return "low"
    return "very_low"


def analyze_frequency(
    expression: str,
    window_days: int = 30,
) -> FrequencyResult:
    """Estimate how often *expression* fires and classify its frequency tier."""
    try:
        parse_expression(expression)
    except ParseError as exc:
        return FrequencyResult(
            expression=expression,
            runs_per_day=None,
            runs_per_week=None,
            runs_per_month=None,
            category="unknown",
            error=str(exc),
        )

    est = estimate_runs(expression, window_days=window_days)
    if not est.ok():
        return FrequencyResult(
            expression=expression,
            runs_per_day=None,
            runs_per_week=None,
            runs_per_month=None,
            category="unknown",
            error=est.error,
        )

    total = est.count
    per_day = total / window_days
    per_week = per_day * 7
    per_month = per_day * 30
    category = _categorize(per_day)

    warnings: List[str] = []
    if category == "very_high":
        warnings.append("Expression fires very frequently; ensure the job is lightweight.")
    if category == "very_low":
        warnings.append("Expression fires rarely; verify this is intentional.")

    return FrequencyResult(
        expression=expression,
        runs_per_day=round(per_day, 4),
        runs_per_week=round(per_week, 4),
        runs_per_month=round(per_month, 4),
        category=category,
        warnings=warnings,
    )


def compare_frequencies(
    expressions: List[str],
    window_days: int = 30,
) -> List[FrequencyResult]:
    """Return a FrequencyResult for each expression, sorted highest-to-lowest."""
    results = [analyze_frequency(e, window_days=window_days) for e in expressions]
    results.sort(
        key=lambda r: r.runs_per_day if r.runs_per_day is not None else -1,
        reverse=True,
    )
    return results
