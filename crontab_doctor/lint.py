"""Linter for crontab expressions — detects suspicious or risky patterns."""

from dataclasses import dataclass, field
from typing import List

from .parser import CronExpression, parse_expression, ParseError


@dataclass
class LintWarning:
    code: str
    message: str
    severity: str = "warning"  # 'warning' | 'info'

    def __repr__(self) -> str:
        return f"LintWarning({self.code!r}, {self.message!r}, severity={self.severity!r})"


_MIDNIGHT_HEAVY_MINUTES = {0}
_HEAVY_HOURS = {0, 1, 2, 3}


def _check_too_frequent(expr: CronExpression) -> List[LintWarning]:
    """Warn when a job runs more often than every minute (i.e. wildcard on minute)."""
    warnings: List[LintWarning] = []
    if expr.minute == "*" and expr.hour == "*":
        warnings.append(LintWarning(
            code="L001",
            message="Expression runs every minute — verify this is intentional.",
            severity="warning",
        ))
    return warnings


def _check_midnight_congestion(expr: CronExpression) -> List[LintWarning]:
    """Warn when many jobs are likely scheduled at midnight (minute=0, hour=0)."""
    warnings: List[LintWarning] = []
    if expr.minute == "0" and expr.hour == "0":
        warnings.append(LintWarning(
            code="L002",
            message="Job is scheduled at midnight (00:00) — a common congestion point.",
            severity="info",
        ))
    return warnings


def _check_day_and_weekday_both_set(expr: CronExpression) -> List[LintWarning]:
    """Warn when both day-of-month and day-of-week are restricted (OR semantics)."""
    warnings: List[LintWarning] = []
    if expr.day != "*" and expr.weekday != "*":
        warnings.append(LintWarning(
            code="L003",
            message=(
                "Both day-of-month and day-of-week are set; cron uses OR semantics, "
                "which may cause the job to run more often than expected."
            ),
            severity="warning",
        ))
    return warnings


def _check_large_step(expr: CronExpression) -> List[LintWarning]:
    """Warn about step values that may produce unexpected single-execution behaviour."""
    warnings: List[LintWarning] = []
    for fname, fval, max_val in [
        ("minute", expr.minute, 59),
        ("hour", expr.hour, 23),
    ]:
        if "/" in str(fval):
            try:
                step = int(str(fval).split("/")[1])
                if step > max_val // 2:
                    warnings.append(LintWarning(
                        code="L004",
                        message=(
                            f"Step value /{step} on '{fname}' is large and may result "
                            "in only one execution per cycle."
                        ),
                        severity="info",
                    ))
            except (ValueError, IndexError):
                pass
    return warnings


_CHECKS = [
    _check_too_frequent,
    _check_midnight_congestion,
    _check_day_and_weekday_both_set,
    _check_large_step,
]


def lint_expression(raw: str) -> List[LintWarning]:
    """Run all lint checks against *raw* and return a (possibly empty) list of warnings."""
    try:
        expr = parse_expression(raw)
    except ParseError:
        return []  # parser/validator already surfaces errors

    warnings: List[LintWarning] = []
    for check in _CHECKS:
        warnings.extend(check(expr))
    return warnings
