"""Detect anomalous cron expressions that are syntactically valid but semantically suspicious."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse_expression, ParseError
from .next_run import next_runs, NextRunError


@dataclass
class AnomalyWarning:
    code: str
    message: str
    severity: str = "warning"  # "info" | "warning" | "critical"

    def __repr__(self) -> str:
        return f"AnomalyWarning(code={self.code!r}, severity={self.severity!r}, message={self.message!r})"


@dataclass
class AnomalyResult:
    expression: str
    warnings: List[AnomalyWarning] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"[ERROR] {self.error}"
        if not self.warnings:
            return f"No anomalies detected in '{self.expression}'."
        lines = [f"Anomalies detected in '{self.expression}':"]
        for w in self.warnings:
            lines.append(f"  [{w.severity.upper()}] {w.code}: {w.message}")
        return "\n".join(lines)


def _check_feb_31(expr) -> Optional[AnomalyWarning]:
    """Warn when day-of-month includes 29-31 and month is fixed to February."""
    month_field = expr.month
    dom_field = expr.day_of_month
    if month_field == "2" or month_field == "02":
        for part in dom_field.split(","):
            part = part.strip()
            if part in ("29", "30", "31"):
                return AnomalyWarning(
                    code="IMPOSSIBLE_DATE",
                    message=f"Day {part} never exists in February; this job may never run.",
                    severity="critical",
                )
    return None


def _check_no_next_run(expression: str) -> Optional[AnomalyWarning]:
    """Warn if we cannot compute any next run within a 4-year window."""
    try:
        runs = next_runs(expression, count=1, max_years=4)
        if not runs:
            return AnomalyWarning(
                code="NO_NEXT_RUN",
                message="No scheduled run found within the next 4 years.",
                severity="critical",
            )
    except NextRunError:
        pass
    return None


def _check_leap_only(expr) -> Optional[AnomalyWarning]:
    """Warn when expression only fires on Feb 29 (leap day)."""
    if expr.month in ("2", "02") and expr.day_of_month == "29":
        return AnomalyWarning(
            code="LEAP_DAY_ONLY",
            message="Expression fires only on Feb 29 (leap day); runs at most once every 4 years.",
            severity="warning",
        )
    return None


def detect_anomalies(expression: str) -> AnomalyResult:
    """Run all anomaly checks against *expression* and return an AnomalyResult."""
    try:
        expr = parse_expression(expression)
    except ParseError as exc:
        return AnomalyResult(expression=expression, error=str(exc))

    warnings: List[AnomalyWarning] = []

    for check in (_check_feb_31, _check_leap_only):
        w = check(expr)
        if w:
            warnings.append(w)

    w = _check_no_next_run(expression)
    if w:
        warnings.append(w)

    return AnomalyResult(expression=expression, warnings=warnings)
