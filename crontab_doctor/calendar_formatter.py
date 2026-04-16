"""Format CalendarResult for terminal output."""
from __future__ import annotations
from .cron_calendar import CalendarResult

_RESET = "\033[0m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_GREEN = "\033[32m"


def _c(code: str, text: str, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_calendar(result: CalendarResult, color: bool = True) -> str:
    lines: list[str] = []
    if not result.ok:
        lines.append(_c(_RED, f"✖ {result.error}", color))
        return "\n".join(lines)

    if not result.entries:
        lines.append(_c(_YELLOW, "No expressions provided.", color))
        return "\n".join(lines)

    for entry in result.entries:
        header = entry.label or entry.expression
        lines.append(_c(_BOLD + _CYAN, f"● {header}", color))
        if entry.label:
            lines.append(f"  Expression : {entry.expression}")
        if not entry.runs:
            lines.append(_c(_YELLOW, "  No runs in window.", color))
        else:
            for dt in entry.runs:
                lines.append(_c(_GREEN, f"  ✓ {dt.strftime('%Y-%m-%d %H:%M')}", color))
        lines.append("")

    lines.append(_c(_BOLD, result.summary(), color))
    return "\n".join(lines)
