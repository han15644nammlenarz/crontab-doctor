"""Alert threshold checker: warn when a cron job runs too often or too rarely."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from crontab_doctor.run_estimator import estimate_runs
import datetime


@dataclass
class ThresholdResult:
    expression: str
    min_runs: Optional[int]
    max_runs: Optional[int]
    actual_runs: Optional[int]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def ok(self) -> bool:
        return not self.errors

    def summary(self) -> str:
        if self.errors:
            return f"[ERROR] {'; '.join(self.errors)}"
        parts = [f"Expression: {self.expression}"]
        parts.append(f"Runs in window: {self.actual_runs}")
        for w in self.warnings:
            parts.append(f"[WARN] {w}")
        if not self.warnings:
            parts.append("All thresholds satisfied.")
        return "\n".join(parts)


def check_threshold(
    expression: str,
    *,
    hours: int = 24,
    min_runs: Optional[int] = None,
    max_runs: Optional[int] = None,
) -> ThresholdResult:
    """Estimate runs in *hours* window and compare against min/max thresholds."""
    now = datetime.datetime.now()
    end = now + datetime.timedelta(hours=hours)
    est = estimate_runs(expression, start=now, end=end)
    if not est.ok():
        return ThresholdResult(
            expression=expression,
            min_runs=min_runs,
            max_runs=max_runs,
            actual_runs=None,
            errors=[est.error or "estimation failed"],
        )
    actual = est.run_count
    warnings: List[str] = []
    if min_runs is not None and actual < min_runs:
        warnings.append(
            f"Job runs {actual}x in {hours}h window, below minimum of {min_runs}."
        )
    if max_runs is not None and actual > max_runs:
        warnings.append(
            f"Job runs {actual}x in {hours}h window, exceeds maximum of {max_runs}."
        )
    return ThresholdResult(
        expression=expression,
        min_runs=min_runs,
        max_runs=max_runs,
        actual_runs=actual,
        warnings=warnings,
    )
