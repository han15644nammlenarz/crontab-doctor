"""Overlap reporter: summarises scheduling overlaps between cron expressions."""

from dataclasses import dataclass, field
from typing import List, Tuple

from .conflict_detector import Conflict, detect_conflicts
from .parser import CronExpression


@dataclass
class OverlapReport:
    """Aggregated overlap report for a collection of expressions."""

    expressions: List[CronExpression]
    conflicts: List[Conflict] = field(default_factory=list)
    error: str = ""

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        total = len(self.conflicts)
        if total == 0:
            return "No overlapping schedules detected."
        pairs: List[str] = []
        for c in self.conflicts:
            pairs.append(f"  - {c.expression_a!r} overlaps with {c.expression_b!r}")
        body = "\n".join(pairs)
        noun = "overlap" if total == 1 else "overlaps"
        return f"{total} schedule {noun} detected:\n{body}"


def build_overlap_report(raw_expressions: List[str]) -> OverlapReport:
    """Parse *raw_expressions* and detect pairwise schedule overlaps."""
    from .parser import parse_expression, ParseError

    parsed: List[CronExpression] = []
    for raw in raw_expressions:
        try:
            parsed.append(parse_expression(raw))
        except ParseError as exc:
            return OverlapReport(expressions=[], error=str(exc))

    conflicts = detect_conflicts(parsed)
    return OverlapReport(expressions=parsed, conflicts=conflicts)
