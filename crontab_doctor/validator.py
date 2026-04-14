"""Crontab field validation logic."""

import re
from typing import List

from .parser import CronExpression, CronField, ParseError


@dataclass_workaround = None  # noqa — using plain classes


class ValidationError:
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message

    def __repr__(self):
        return f"ValidationError(field={self.field!r}, message={self.message!r})"


def _validate_value(value: int, field: CronField) -> bool:
    return field.min_val <= value <= field.max_val


def _parse_segment(segment: str, field: CronField) -> List[ValidationError]:
    errors = []
    name = field.name

    # Wildcard
    if segment == "*":
        return errors

    # Step: */n or x/n
    step_match = re.fullmatch(r"(\*|\d+)/(\d+)", segment)
    if step_match:
        step = int(step_match.group(2))
        if step == 0:
            errors.append(ValidationError(name, f"Step value cannot be zero in '{segment}'"))
        base = step_match.group(1)
        if base != "*":
            val = int(base)
            if not _validate_value(val, field):
                errors.append(ValidationError(name, f"Value {val} out of range [{field.min_val}-{field.max_val}]"))
        return errors

    # Range: x-y
    range_match = re.fullmatch(r"(\d+)-(\d+)", segment)
    if range_match:
        low, high = int(range_match.group(1)), int(range_match.group(2))
        if not _validate_value(low, field):
            errors.append(ValidationError(name, f"Range start {low} out of range [{field.min_val}-{field.max_val}]"))
        if not _validate_value(high, field):
            errors.append(ValidationError(name, f"Range end {high} out of range [{field.min_val}-{field.max_val}]"))
        if low > high:
            errors.append(ValidationError(name, f"Range start {low} is greater than end {high}"))
        return errors

    # Plain integer
    int_match = re.fullmatch(r"\d+", segment)
    if int_match:
        val = int(segment)
        if not _validate_value(val, field):
            errors.append(ValidationError(name, f"Value {val} out of range [{field.min_val}-{field.max_val}]"))
        return errors

    errors.append(ValidationError(name, f"Unrecognized segment syntax: '{segment}'"))
    return errors


def validate_expression(expr: CronExpression) -> List[ValidationError]:
    """Validate all fields of a parsed cron expression."""
    errors = []
    for field in expr.fields:
        segments = field.raw.split(",")
        for segment in segments:
            errors.extend(_parse_segment(segment.strip(), field))
    return errors
