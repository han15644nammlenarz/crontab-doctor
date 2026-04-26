"""pattern_suggester.py — Suggest canonical cron patterns based on a natural-language description or an existing expression.

Given a free-text intent (e.g. "every weekday at 9am") or a raw cron
expression, this module returns a ranked list of close canonical patterns
from a built-in catalogue, together with a human-readable rationale.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse_expression, ParseError

# ---------------------------------------------------------------------------
# Catalogue of canonical patterns
# ---------------------------------------------------------------------------

# Each entry: (expression, short_description, tags)
_CATALOGUE: List[tuple] = [
    ("* * * * *",   "Every minute",                          ["frequent", "debug"]),
    ("*/5 * * * *", "Every 5 minutes",                       ["frequent"]),
    ("*/10 * * * *","Every 10 minutes",                      ["frequent"]),
    ("*/15 * * * *","Every 15 minutes",                      ["frequent"]),
    ("*/30 * * * *","Every 30 minutes",                      ["frequent"]),
    ("0 * * * *",   "Every hour (on the hour)",              ["hourly"]),
    ("0 */2 * * *", "Every 2 hours",                         ["hourly"]),
    ("0 */6 * * *", "Every 6 hours",                         ["hourly"]),
    ("0 */12 * * *","Twice a day (every 12 hours)",           ["daily"]),
    ("0 0 * * *",   "Once a day at midnight",                ["daily", "midnight"]),
    ("0 6 * * *",   "Every day at 6 AM",                     ["daily", "morning"]),
    ("0 9 * * *",   "Every day at 9 AM",                     ["daily", "morning"]),
    ("0 12 * * *",  "Every day at noon",                     ["daily", "noon"]),
    ("0 18 * * *",  "Every day at 6 PM",                     ["daily", "evening"]),
    ("0 9 * * 1-5", "Weekdays at 9 AM",                      ["weekday", "morning"]),
    ("0 9 * * 1",   "Every Monday at 9 AM",                  ["weekly", "monday"]),
    ("0 0 * * 0",   "Every Sunday at midnight",              ["weekly", "sunday"]),
    ("0 0 * * 1",   "Every Monday at midnight",              ["weekly", "monday"]),
    ("0 0 1 * *",   "First day of every month at midnight",  ["monthly"]),
    ("0 0 15 * *",  "15th of every month at midnight",       ["monthly"]),
    ("0 0 1 1 *",   "Once a year on Jan 1st at midnight",    ["yearly", "annual"]),
    ("0 0 1 */3 *", "First day of every quarter at midnight",["quarterly"]),
    ("@reboot",     "Once at system reboot",                 ["reboot", "startup"]),
]

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Suggestion:
    """A single pattern suggestion."""
    expression: str
    description: str
    tags: List[str]
    score: float          # 0.0 – 1.0, higher is more relevant
    rationale: str        # human-readable reason this was surfaced

    def __repr__(self) -> str:  # pragma: no cover
        return f"Suggestion({self.expression!r}, score={self.score:.2f})"


@dataclass
class SuggestionResult:
    """Result returned by :func:`suggest_patterns`."""
    query: str
    suggestions: List[Suggestion] = field(default_factory=list)
    error: Optional[str] = None

    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if not self.suggestions:
            return f"No suggestions found for {self.query!r}."
        top = self.suggestions[0]
        return (
            f"Top suggestion for {self.query!r}: "
            f"{top.expression!r} — {top.description} (score {top.score:.2f})"
        )

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_KEYWORD_TAG_MAP = {
    "minute":   ["frequent"],
    "frequent": ["frequent"],
    "hour":     ["hourly"],
    "hourly":   ["hourly"],
    "daily":    ["daily"],
    "day":      ["daily"],
    "midnight": ["midnight", "daily"],
    "morning":  ["morning"],
    "noon":     ["noon"],
    "evening":  ["evening"],
    "night":    ["evening"],
    "weekday":  ["weekday"],
    "weekly":   ["weekly"],
    "week":     ["weekly"],
    "monday":   ["monday", "weekly"],
    "sunday":   ["sunday", "weekly"],
    "monthly":  ["monthly"],
    "month":    ["monthly"],
    "quarterly":["quarterly"],
    "quarter":  ["quarterly"],
    "yearly":   ["yearly"],
    "annual":   ["yearly"],
    "year":     ["yearly"],
    "reboot":   ["reboot"],
    "startup":  ["startup", "reboot"],
    "boot":     ["reboot"],
}


def _tags_from_query(query: str) -> List[str]:
    """Extract relevant catalogue tags from a free-text query."""
    words = re.findall(r"[a-z]+", query.lower())
    tags: List[str] = []
    for word in words:
        tags.extend(_KEYWORD_TAG_MAP.get(word, []))
    return list(dict.fromkeys(tags))  # deduplicate, preserve order


def _score_entry(
    expr: str,
    desc: str,
    entry_tags: List[str],
    query_tags: List[str],
    parsed_fields: Optional[list],
) -> tuple[float, str]:
    """Return (score, rationale) for a catalogue entry."""
    if not query_tags and parsed_fields is None:
        # No signal — return uniform low score
        return 0.1, "No specific signal; generic suggestion."

    matched = [t for t in query_tags if t in entry_tags]
    if not matched:
        return 0.0, ""

    score = min(1.0, len(matched) / max(len(query_tags), 1))
    rationale = f"Matched keyword(s): {', '.join(matched)}."
    return round(score, 3), rationale


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def suggest_patterns(
    query: str,
    top_n: int = 5,
) -> SuggestionResult:
    """Return up to *top_n* canonical cron pattern suggestions for *query*.

    *query* may be:
    - A natural-language description, e.g. ``"every weekday morning"``.
    - A (possibly broken) cron expression — suggestions will be semantically
      close alternatives from the catalogue.

    Parameters
    ----------
    query:
        Free-text intent or existing cron expression.
    top_n:
        Maximum number of suggestions to return (default 5).
    """
    if not query or not query.strip():
        return SuggestionResult(query=query, error="Query must not be empty.")

    # Try to parse as an expression to extract field information
    parsed_fields: Optional[list] = None
    try:
        expr = parse_expression(query.strip())
        parsed_fields = [
            expr.minute, expr.hour, expr.day_of_month,
            expr.month, expr.day_of_week,
        ]
    except (ParseError, Exception):
        pass  # treat as natural-language query

    query_tags = _tags_from_query(query)

    scored: List[Suggestion] = []
    for expr_str, desc, tags in _CATALOGUE:
        score, rationale = _score_entry(
            expr_str, desc, tags, query_tags, parsed_fields
        )
        if score > 0.0:
            scored.append(
                Suggestion(
                    expression=expr_str,
                    description=desc,
                    tags=tags,
                    score=score,
                    rationale=rationale,
                )
            )

    # If nothing matched by tags, surface generic high-value patterns
    if not scored:
        for expr_str, desc, tags in _CATALOGUE[:5]:
            scored.append(
                Suggestion(
                    expression=expr_str,
                    description=desc,
                    tags=tags,
                    score=0.05,
                    rationale="Generic fallback suggestion.",
                )
            )

    scored.sort(key=lambda s: s.score, reverse=True)
    return SuggestionResult(query=query, suggestions=scored[:top_n])
