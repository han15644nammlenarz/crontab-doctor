"""Generate a heatmap of cron job activity across hours and days."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from crontab_doctor.next_run import next_runs
from crontab_doctor.parser import parse_expression, ParseError

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HOURS = list(range(24))


@dataclass
class HeatmapResult:
    expression: str
    error: Optional[str]
    # grid[day_index][hour] = count
    grid: Dict[int, Dict[int, int]] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if not self.ok:
            return f"Heatmap error for '{self.expression}': {self.error}"
        total = sum(v for row in self.grid.values() for v in row.values())
        return f"Heatmap for '{self.expression}': {total} runs over sampled window"


def build_heatmap(
    expression: str,
    label: Optional[str] = None,
    days_ahead: int = 7,
) -> HeatmapResult:
    """Count how many times a cron fires per (weekday, hour) over *days_ahead* days."""
    try:
        parse_expression(expression)
    except ParseError as exc:
        return HeatmapResult(expression=expression, error=str(exc))

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    minutes_ahead = days_ahead * 24 * 60

    try:
        runs = next_runs(expression, count=minutes_ahead, after=now)
    except Exception as exc:  # noqa: BLE001
        return HeatmapResult(expression=expression, error=str(exc))

    grid: Dict[int, Dict[int, int]] = {d: {h: 0 for h in HOURS} for d in range(7)}
    for dt in runs:
        # weekday(): Monday=0 … Sunday=6
        grid[dt.weekday()][dt.hour] += 1

    return HeatmapResult(expression=expression, error=None, grid=grid)
