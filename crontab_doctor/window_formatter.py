"""Format WindowResult objects for CLI output."""
from __future__ import annotations

from .window_analyzer import WindowResult

_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _c(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}"


def format_window_result(result: WindowResult, color: bool = True) -> str:
    lines: list[str] = []

    header = f"Window analysis: {result.expression}"
    lines.append(_c(header, _BOLD) if color else header)

    span = int((result.window_end - result.window_start).total_seconds() / 60)
    lines.append(
        f"  From : {result.window_start.strftime('%Y-%m-%d %H:%M')}"
    )
    lines.append(
        f"  Until: {result.window_end.strftime('%Y-%m-%d %H:%M')}  ({span} min)"
    )

    if result.error:
        msg = f"  ✗ {result.error}"
        lines.append(_c(msg, _RED) if color else msg)
        return "\n".join(lines)

    count = len(result.fires)
    if count == 0:
        msg = "  ✗ Does not fire within this window"
        lines.append(_c(msg, _YELLOW) if color else msg)
    else:
        noun = "firing" if count == 1 else "firings"
        msg = f"  ✓ {count} {noun} scheduled:"
        lines.append(_c(msg, _GREEN) if color else msg)
        for dt in result.fires:
            lines.append(f"      • {dt.strftime('%Y-%m-%d %H:%M')}")  

    return "\n".join(lines)
