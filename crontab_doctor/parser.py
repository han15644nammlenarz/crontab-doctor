"""Crontab expression parser module."""

import re
from dataclasses import dataclass
from typing import Optional

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),
}

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DOW_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}

SPECIAL_EXPRESSIONS = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


@dataclass
class CronField:
    name: str
    raw: str
    min_val: int
    max_val: int


@dataclass
class CronExpression:
    raw: str
    fields: list
    command: Optional[str] = None


class ParseError(ValueError):
    pass


def resolve_aliases(value: str, field_name: str) -> str:
    """Replace named aliases with numeric equivalents."""
    if field_name == "month":
        for alias, num in MONTH_ALIASES.items():
            value = re.sub(rf"\b{alias}\b", str(num), value, flags=re.IGNORECASE)
    elif field_name == "day_of_week":
        for alias, num in DOW_ALIASES.items():
            value = re.sub(rf"\b{alias}\b", str(num), value, flags=re.IGNORECASE)
    return value


def parse_expression(expression: str) -> CronExpression:
    """Parse a crontab expression string into a CronExpression object."""
    expression = expression.strip()

    if expression in SPECIAL_EXPRESSIONS:
        expression = SPECIAL_EXPRESSIONS[expression]

    parts = expression.split()
    if len(parts) < 5:
        raise ParseError(
            f"Expected at least 5 fields, got {len(parts)}: '{expression}'"
        )

    command = " ".join(parts[5:]) if len(parts) > 5 else None
    field_parts = parts[:5]

    fields = []
    for i, (name, part) in enumerate(zip(FIELD_NAMES, field_parts)):
        min_val, max_val = FIELD_RANGES[name]
        resolved = resolve_aliases(part, name)
        fields.append(CronField(name=name, raw=resolved, min_val=min_val, max_val=max_val))

    return CronExpression(raw=expression, fields=fields, command=command)
