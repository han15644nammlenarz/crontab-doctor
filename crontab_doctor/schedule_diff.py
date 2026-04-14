"""Compare two cron expressions and highlight scheduling differences."""

from dataclasses import dataclass, field
from typing import List, Tuple

from .next_run import next_runs, NextRunError
from .parser import parse_expression, ParseError


@dataclass
class ScheduleDiff:
    expr_a: str
    expr_b: str
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    shared: List[str] = field(default_factory=list)
    error: str = ""

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        lines = [
            f"Comparing: '{self.expr_a}'  vs  '{self.expr_b}'",
            f"  Shared run times   : {len(self.shared)}",
            f"  Only in first      : {len(self.only_in_a)}",
            f"  Only in second     : {len(self.only_in_b)}",
        ]
        if self.shared:
            lines.append("  Sample shared      : " + ", ".join(self.shared[:3]))
        if self.only_in_a:
            lines.append("  Sample first-only  : " + ", ".join(self.only_in_a[:3]))
        if self.only_in_b:
            lines.append("  Sample second-only : " + ", ".join(self.only_in_b[:3]))
        return "\n".join(lines)


def diff_expressions(
    expr_a: str,
    expr_b: str,
    *,
    count: int = 20,
) -> ScheduleDiff:
    """Return a ScheduleDiff comparing the next *count* runs of two expressions."""
    result = ScheduleDiff(expr_a=expr_a, expr_b=expr_b)

    try:
        parse_expression(expr_a)
    except ParseError as exc:
        result.error = f"Invalid first expression: {exc}"
        return result

    try:
        parse_expression(expr_b)
    except ParseError as exc:
        result.error = f"Invalid second expression: {exc}"
        return result

    try:
        runs_a: List[str] = [
            dt.strftime("%Y-%m-%d %H:%M") for dt in next_runs(expr_a, count=count)
        ]
        runs_b: List[str] = [
            dt.strftime("%Y-%m-%d %H:%M") for dt in next_runs(expr_b, count=count)
        ]
    except NextRunError as exc:
        result.error = str(exc)
        return result

    set_a = set(runs_a)
    set_b = set(runs_b)

    result.shared = sorted(set_a & set_b)
    result.only_in_a = sorted(set_a - set_b)
    result.only_in_b = sorted(set_b - set_a)
    return result
