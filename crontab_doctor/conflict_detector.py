"""Detect scheduling conflicts between multiple cron expressions."""

from dataclasses import dataclass, field
from typing import List, Tuple
from .parser import CronExpression


@dataclass
class Conflict:
    expr_a: str
    expr_b: str
    reason: str

    def __repr__(self) -> str:
        return f"Conflict({self.expr_a!r} vs {self.expr_b!r}: {self.reason})"


def _expand_field(value: str, min_val: int, max_val: int) -> set:
    """Expand a cron field into a set of matching integers."""
    if value == "*":
        return set(range(min_val, max_val + 1))

    result = set()
    for part in value.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            start = min_val if base == "*" else int(base.split("-")[0])
            end = max_val if base == "*" else (int(base.split("-")[1]) if "-" in base else max_val)
            result.update(range(start, end + 1, step))
        elif "-" in part:
            lo, hi = part.split("-", 1)
            result.update(range(int(lo), int(hi) + 1))
        else:
            result.add(int(part))
    return result


def _expressions_overlap(a: CronExpression, b: CronExpression) -> bool:
    """Return True if two expressions can fire at the same minute."""
    ranges = [
        (a.minute,  b.minute,  0, 59),
        (a.hour,    b.hour,    0, 23),
        (a.dom,     b.dom,     1, 31),
        (a.month,   b.month,   1, 12),
        (a.dow,     b.dow,     0,  7),
    ]
    for fa, fb, lo, hi in ranges:
        if not (_expand_field(fa, lo, hi) & _expand_field(fb, lo, hi)):
            return False
    return True


def detect_conflicts(expressions: List[Tuple[str, CronExpression]]) -> List[Conflict]:
    """Given a list of (raw_expr, CronExpression) pairs, return all pairwise conflicts."""
    conflicts: List[Conflict] = []
    items = list(expressions)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            raw_a, expr_a = items[i]
            raw_b, expr_b = items[j]
            if _expressions_overlap(expr_a, expr_b):
                conflicts.append(
                    Conflict(
                        expr_a=raw_a,
                        expr_b=raw_b,
                        reason="Both expressions can fire at the same minute",
                    )
                )
    return conflicts
