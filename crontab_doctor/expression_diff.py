"""Compare two cron expressions field-by-field and report differences."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse_expression, ParseError


@dataclass
class FieldDiff:
    """Difference in a single cron field."""
    field_name: str
    left: str
    right: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"FieldDiff({self.field_name}: {self.left!r} -> {self.right!r})"


@dataclass
class ExpressionDiff:
    """Result of comparing two cron expressions."""
    left: str
    right: str
    field_diffs: List[FieldDiff] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def identical(self) -> bool:
        return self.error is None and len(self.field_diffs) == 0

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if self.identical:
            return "Expressions are identical."
        lines = [f"Differences between '{self.left}' and '{self.right}':"]
        for d in self.field_diffs:
            lines.append(f"  {d.field_name:10s}: {d.left!r:20s} -> {d.right!r}")
        return "\n".join(lines)


_FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


def diff_expressions(left: str, right: str) -> ExpressionDiff:
    """Parse both expressions and diff their fields."""
    try:
        expr_left = parse_expression(left)
    except ParseError as exc:
        return ExpressionDiff(left=left, right=right, error=f"Invalid left expression: {exc}")

    try:
        expr_right = parse_expression(right)
    except ParseError as exc:
        return ExpressionDiff(left=left, right=right, error=f"Invalid right expression: {exc}")

    left_fields = [
        expr_left.minute,
        expr_left.hour,
        expr_left.day_of_month,
        expr_left.month,
        expr_left.day_of_week,
    ]
    right_fields = [
        expr_right.minute,
        expr_right.hour,
        expr_right.day_of_month,
        expr_right.month,
        expr_right.day_of_week,
    ]

    diffs = [
        FieldDiff(name, lf, rf)
        for name, lf, rf in zip(_FIELD_NAMES, left_fields, right_fields)
        if lf != rf
    ]

    return ExpressionDiff(left=left, right=right, field_diffs=diffs)
