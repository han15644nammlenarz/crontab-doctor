"""Compute the next scheduled run time(s) for a cron expression."""

from datetime import datetime, timedelta
from typing import List, Optional

from .parser import CronExpression, parse_expression
from .conflict_detector import _expand_field


class NextRunError(Exception):
    """Raised when next run time cannot be computed."""


def _next_run_from(
    expr: CronExpression,
    after: datetime,
    limit: int = 5,
) -> List[datetime]:
    """Return up to *limit* future datetimes matching *expr* after *after*.

    Searches forward minute-by-minute for up to one year.
    """
    minutes = _expand_field(expr.minute, 0, 59)
    hours = _expand_field(expr.hour, 0, 23)
    days = _expand_field(expr.day_of_month, 1, 31)
    months = _expand_field(expr.month, 1, 12)
    weekdays = _expand_field(expr.day_of_week, 0, 6)

    results: List[datetime] = []
    # Start from the next whole minute after *after*
    candidate = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
    deadline = after + timedelta(days=366)

    while candidate <= deadline and len(results) < limit:
        if (
            candidate.month in months
            and candidate.day in days
            and candidate.weekday() % 7 in weekdays  # Python Mon=0; cron Sun=0
            and candidate.hour in hours
            and candidate.minute in minutes
        ):
            results.append(candidate)
            candidate += timedelta(minutes=1)
        else:
            candidate += timedelta(minutes=1)

    if not results:
        raise NextRunError(
            f"No matching run time found within one year for: {expr.raw}"
        )
    return results


def next_runs(
    expression: str,
    after: Optional[datetime] = None,
    count: int = 5,
) -> List[datetime]:
    """Parse *expression* and return the next *count* scheduled datetimes.

    Args:
        expression: A cron expression string (5-field or @alias).
        after: Reference datetime (defaults to ``datetime.now()``).
        count: How many future run times to return.

    Returns:
        List of upcoming :class:`datetime` objects.

    Raises:
        ParseError: If the expression cannot be parsed.
        NextRunError: If no matching time is found within one year.
    """
    if after is None:
        after = datetime.now()
    expr = parse_expression(expression)
    return _next_run_from(expr, after, limit=count)
