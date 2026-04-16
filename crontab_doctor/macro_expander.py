"""Expand cron macro shortcuts into standard 5-field expressions."""

from dataclasses import dataclass, field
from typing import Optional


BUILTIN_MACROS: dict[str, str] = {
    "every_minute": "* * * * *",
    "every_5_minutes": "*/5 * * * *",
    "every_10_minutes": "*/10 * * * *",
    "every_15_minutes": "*/15 * * * *",
    "every_30_minutes": "*/30 * * * *",
    "hourly": "0 * * * *",
    "daily": "0 0 * * *",
    "daily_noon": "0 12 * * *",
    "weekly": "0 0 * * 0",
    "monthly": "0 0 1 * *",
    "yearly": "0 0 1 1 *",
    "weekdays": "0 9 * * 1-5",
    "weekends": "0 10 * * 6,0",
    "business_hours": "0 9-17 * * 1-5",
}


@dataclass
class MacroExpansion:
    name: str
    original: str
    expanded: str
    description: str = ""
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if not self.ok:
            return f"[ERROR] {self.name}: {self.error}"
        lines = [f"Macro : {self.name}"]
        if self.description:
            lines.append(f"Desc  : {self.description}")
        lines.append(f"Input : {self.original}")
        lines.append(f"Output: {self.expanded}")
        return "\n".join(lines)


_DESCRIPTIONS: dict[str, str] = {
    "every_minute": "Runs every minute",
    "every_5_minutes": "Runs every 5 minutes",
    "every_10_minutes": "Runs every 10 minutes",
    "every_15_minutes": "Runs every 15 minutes",
    "every_30_minutes": "Runs every 30 minutes",
    "hourly": "Runs at the start of every hour",
    "daily": "Runs at midnight every day",
    "daily_noon": "Runs at noon every day",
    "weekly": "Runs at midnight every Sunday",
    "monthly": "Runs at midnight on the 1st of each month",
    "yearly": "Runs at midnight on January 1st",
    "weekdays": "Runs at 9 AM on weekdays",
    "weekends": "Runs at 10 AM on weekends",
    "business_hours": "Runs every hour during business hours on weekdays",
}


def list_macros() -> list[str]:
    return sorted(BUILTIN_MACROS.keys())


def expand_macro(name: str) -> MacroExpansion:
    if name not in BUILTIN_MACROS:
        return MacroExpansion(
            name=name,
            original=name,
            expanded="",
            error=f"Unknown macro '{name}'. Use list_macros() to see available macros.",
        )
    expanded = BUILTIN_MACROS[name]
    return MacroExpansion(
        name=name,
        original=name,
        expanded=expanded,
        description=_DESCRIPTIONS.get(name, ""),
    )
