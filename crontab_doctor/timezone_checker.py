"""Timezone-awareness checker for cron expressions."""
from __future__ import annotations

import dataclasses
from typing import List, Optional

try:
    import zoneinfo
except ImportError:  # Python < 3.9
    from backports import zoneinfo  # type: ignore

from .parser import CronExpression, ParseError, parse_expression


@dataclasses.dataclass
class TzCheckResult:
    expression: str
    timezone: Optional[str]
    timezone_valid: bool
    warnings: List[str] = dataclasses.field(default_factory=list)
    errors: List[str] = dataclasses.field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and self.timezone_valid

    def summary(self) -> str:
        parts = [f"Expression : {self.expression}"]
        parts.append(f"Timezone   : {self.timezone or '(none — system local)'}")
        if self.timezone_valid:
            parts.append("TZ status  : valid")
        else:
            parts.append("TZ status  : INVALID")
        for w in self.warnings:
            parts.append(f"  warning  : {w}")
        for e in self.errors:
            parts.append(f"  error    : {e}")
        return "\n".join(parts)


def _available_timezones() -> frozenset:
    try:
        return zoneinfo.available_timezones()
    except Exception:
        return frozenset()


def check_timezone(expression: str, timezone: Optional[str] = None) -> TzCheckResult:
    """Validate *expression* and check whether *timezone* is a known IANA zone."""
    warnings: List[str] = []
    errors: List[str] = []

    try:
        parse_expression(expression)
    except ParseError as exc:
        errors.append(str(exc))

    tz_valid = True
    if timezone is not None:
        known = _available_timezones()
        if known and timezone not in known:
            tz_valid = False
            errors.append(f"Unknown timezone '{timezone}'")
        elif not known:
            warnings.append("Cannot verify timezone — zoneinfo database unavailable")

        # Warn about UTC offsets used as IANA names
        if timezone.startswith(("UTC+", "UTC-", "GMT+", "GMT-")):
            warnings.append(
                f"'{timezone}' looks like a fixed offset; prefer an IANA name like "
                "'America/New_York' for DST-aware scheduling"
            )

    return TzCheckResult(
        expression=expression,
        timezone=timezone,
        timezone_valid=tz_valid,
        warnings=warnings,
        errors=errors,
    )
