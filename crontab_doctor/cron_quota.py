"""Quota checker: warn when a set of cron expressions exceeds run-count
or CPU-time budgets within a rolling time window."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .run_estimator import estimate_runs


@dataclass
class QuotaResult:
    expression: str
    runs_in_window: int
    window_hours: int
    max_runs: Optional[int]
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def ok(self) -> bool:
        return self.error is None and len(self.warnings) == 0

    def summary(self) -> str:
        if self.error:
            return f"[ERROR] {self.expression}: {self.error}"
        noun = "run" if self.runs_in_window == 1 else "runs"
        base = (
            f"{self.expression}: {self.runs_in_window} {noun} "
            f"in {self.window_hours}h window"
        )
        if self.warnings:
            return base + " — " + "; ".join(self.warnings)
        return base + " — within quota"


@dataclass
class QuotaReport:
    results: List[QuotaResult] = field(default_factory=list)
    total_runs: int = 0
    global_max: Optional[int] = None
    global_warnings: List[str] = field(default_factory=list)

    def ok(self) -> bool:
        return (
            all(r.ok() for r in self.results)
            and len(self.global_warnings) == 0
        )

    def summary(self) -> str:
        lines = [r.summary() for r in self.results]
        if self.global_warnings:
            lines.append("Global: " + "; ".join(self.global_warnings))
        return "\n".join(lines) if lines else "No expressions checked."


def check_quota(
    expressions: List[str],
    window_hours: int = 24,
    max_runs_per_expression: Optional[int] = None,
    max_runs_total: Optional[int] = None,
) -> QuotaReport:
    """Check each expression against per-expression and global run quotas."""
    if window_hours < 1:
        window_hours = 1

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    results: List[QuotaResult] = []
    total = 0

    for expr in expressions:
        est = estimate_runs(expr, now, window_hours)
        if not est.ok():
            results.append(
                QuotaResult(
                    expression=expr,
                    runs_in_window=0,
                    window_hours=window_hours,
                    max_runs=max_runs_per_expression,
                    error=est.error,
                )
            )
            continue

        count = len(est.run_times)
        total += count
        warnings: List[str] = []

        if max_runs_per_expression is not None and count > max_runs_per_expression:
            warnings.append(
                f"exceeds per-expression limit of {max_runs_per_expression}"
            )

        results.append(
            QuotaResult(
                expression=expr,
                runs_in_window=count,
                window_hours=window_hours,
                max_runs=max_runs_per_expression,
                warnings=warnings,
            )
        )

    global_warnings: List[str] = []
    if max_runs_total is not None and total > max_runs_total:
        global_warnings.append(
            f"total {total} runs exceeds global limit of {max_runs_total}"
        )

    return QuotaReport(
        results=results,
        total_runs=total,
        global_max=max_runs_total,
        global_warnings=global_warnings,
    )
