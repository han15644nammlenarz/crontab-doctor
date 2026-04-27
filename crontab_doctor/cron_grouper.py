"""Group cron expressions by shared schedule characteristics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .parser import parse_expression, ParseError
from .frequency_analyzer import analyze_frequency


@dataclass
class GroupResult:
    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        total = sum(len(v) for v in self.groups.values()) + len(self.ungrouped)
        n = len(self.groups)
        noun = "group" if n == 1 else "groups"
        return (
            f"{total} expression(s) organised into {n} {noun}"
            + (f"; {len(self.ungrouped)} ungrouped" if self.ungrouped else "")
        )


def group_expressions(
    expressions: List[str],
    by: str = "frequency",
) -> GroupResult:
    """Group *expressions* by the chosen strategy.

    Supported strategies
    --------------------
    frequency  – group by coarse frequency category (every-minute, hourly, …)
    hour       – group by the hour field value
    minute     – group by the minute field value
    """
    if by not in ("frequency", "hour", "minute"):
        return GroupResult(error=f"Unknown grouping strategy: {by!r}")

    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = []

    for expr in expressions:
        try:
            parsed = parse_expression(expr)
        except ParseError as exc:
            ungrouped.append(expr)
            continue

        if by == "frequency":
            result = analyze_frequency(expr)
            key = result.category if result.ok() else "unknown"
        elif by == "hour":
            key = parsed.hour
        else:  # minute
            key = parsed.minute

        groups.setdefault(key, []).append(expr)

    return GroupResult(groups=groups, ungrouped=ungrouped)
