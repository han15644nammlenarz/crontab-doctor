"""Estimate compute cost / resource usage for cron schedules."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from crontab_doctor.run_estimator import estimate_runs


@dataclass
class CostEstimate:
    expression: str
    runs_per_day: float
    runs_per_month: float
    cost_per_run: float  # arbitrary unit, e.g. seconds of CPU
    total_daily_cost: float
    total_monthly_cost: float
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"[ERROR] {self.error}"
        lines = [
            f"Expression : {self.expression}",
            f"Runs/day   : {self.runs_per_day:.1f}",
            f"Runs/month : {self.runs_per_month:.1f}",
            f"Cost/run   : {self.cost_per_run:.2f} units",
            f"Daily cost : {self.total_daily_cost:.2f} units",
            f"Monthly    : {self.total_monthly_cost:.2f} units",
        ]
        for w in self.warnings:
            lines.append(f"  ⚠  {w}")
        return "\n".join(lines)


def estimate_cost(
    expression: str,
    cost_per_run: float = 1.0,
    window_hours: int = 24,
) -> CostEstimate:
    """Estimate cost given a cron expression and cost per execution."""
    est = estimate_runs(expression, window_hours=window_hours)
    if not est.ok():
        return CostEstimate(
            expression=expression,
            runs_per_day=0,
            runs_per_month=0,
            cost_per_run=cost_per_run,
            total_daily_cost=0,
            total_monthly_cost=0,
            error=est.error,
        )

    runs_per_day = len(est.run_times)
    runs_per_month = runs_per_day * 30
    daily_cost = runs_per_day * cost_per_run
    monthly_cost = runs_per_month * cost_per_run

    warnings: List[str] = []
    if runs_per_day > 288:
        warnings.append("Very high frequency (>288 runs/day) may incur significant cost.")
    if daily_cost > 1000:
        warnings.append(f"Daily cost exceeds 1000 units ({daily_cost:.1f}).")

    return CostEstimate(
        expression=expression,
        runs_per_day=runs_per_day,
        runs_per_month=runs_per_month,
        cost_per_run=cost_per_run,
        total_daily_cost=daily_cost,
        total_monthly_cost=monthly_cost,
        warnings=warnings,
    )
