"""Search and filter cron expressions by pattern, field value, or label."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse_expression, ParseError


@dataclass
class SearchResult:
    query: str
    matches: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"Search error: {self.error}"
        n = len(self.matches)
        noun = "match" if n == 1 else "matches"
        return f"Query '{self.query}' returned {n} {noun}."


def _expression_matches_field(expression: str, field_index: int, pattern: str) -> bool:
    """Return True if the given field (0-4) of *expression* contains *pattern*."""
    try:
        expr = parse_expression(expression)
    except ParseError:
        return False
    fields = [expr.minute, expr.hour, expr.day_of_month, expr.month, expr.day_of_week]
    if field_index < 0 or field_index >= len(fields):
        return False
    return pattern in fields[field_index]


def search_expressions(
    expressions: List[str],
    query: str,
    *,
    field_index: Optional[int] = None,
) -> SearchResult:
    """Filter *expressions* whose raw text (or a specific field) contains *query*.

    Parameters
    ----------
    expressions:
        List of raw cron expression strings to search.
    query:
        Substring to look for.
    field_index:
        If given (0=minute, 1=hour, 2=dom, 3=month, 4=dow), restrict the
        search to that field only; otherwise the full expression string is
        searched.
    """
    if not query:
        return SearchResult(query=query, error="Query must not be empty.")

    matches: List[str] = []
    for expr in expressions:
        if field_index is not None:
            if _expression_matches_field(expr, field_index, query):
                matches.append(expr)
        else:
            if query in expr:
                matches.append(expr)

    return SearchResult(query=query, matches=matches)
