"""Normalize cron expressions to a canonical form."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .parser import parse_expression, ParseError

# Mapping of common non-standard aliases to their canonical five-field forms
_SPECIAL_ALIASES: dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}

# Canonical month / weekday name -> number
_MONTH_NAMES: dict[str, str] = {
    "jan": "1", "feb": "2", "mar": "3", "apr": "4",
    "may": "5", "jun": "6", "jul": "7", "aug": "8",
    "sep": "9", "oct": "10", "nov": "11", "dec": "12",
}
_WEEKDAY_NAMES: dict[str, str] = {
    "sun": "0", "mon": "1", "tue": "2", "wed": "3",
    "thu": "4", "fri": "5", "sat": "6",
}


@dataclass
class NormalizeResult:
    original: str
    normalized: Optional[str]
    changed: bool
    error: Optional[str] = field(default=None)

    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if self.changed:
            return f"Normalized: {self.original!r} -> {self.normalized!r}"
        return f"Already canonical: {self.original!r}"


def _replace_names(token: str, mapping: dict[str, str]) -> str:
    """Replace named aliases inside a single cron field token."""
    result = token
    for name, number in mapping.items():
        result = result.replace(name, number)
    return result


def _normalize_field(raw: str, mapping: dict[str, str]) -> str:
    """Lower-case and replace named values in a field."""
    return _replace_names(raw.strip().lower(), mapping)


def normalize_expression(expression: str) -> NormalizeResult:
    """Return a canonical five-field cron expression.

    Steps:
    1. Resolve @special aliases.
    2. Replace month / weekday names with numbers.
    3. Validate the result by parsing it.
    """
    expr = expression.strip()

    # Step 1 – special aliases
    lower = expr.lower()
    if lower in _SPECIAL_ALIASES:
        canonical = _SPECIAL_ALIASES[lower]
        return NormalizeResult(original=expression, normalized=canonical, changed=True)

    # Split off optional command (keep only the five schedule fields)
    parts = expr.split()
    if len(parts) < 5:
        return NormalizeResult(
            original=expression, normalized=None, changed=False,
            error=f"Expected at least 5 fields, got {len(parts)}",
        )

    schedule_parts = parts[:5]
    minute, hour, dom, month, dow = schedule_parts

    # Step 2 – replace names
    month_norm = _normalize_field(month, _MONTH_NAMES)
    dow_norm = _normalize_field(dow, _WEEKDAY_NAMES)
    normalized = " ".join([minute, hour, dom, month_norm, dow_norm])

    # Step 3 – validate
    try:
        parse_expression(normalized)
    except ParseError as exc:
        return NormalizeResult(
            original=expression, normalized=None, changed=False,
            error=str(exc),
        )

    changed = normalized != " ".join(schedule_parts)
    return NormalizeResult(original=expression, normalized=normalized, changed=changed)
