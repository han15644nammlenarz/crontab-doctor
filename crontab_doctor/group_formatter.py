"""Formatter for GroupResult objects."""
from __future__ import annotations

from .cron_grouper import GroupResult

_RESET = "\033[0m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_GREEN = "\033[32m"


def _c(code: str, text: str, *, color: bool = True) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_group_result(result: GroupResult, *, color: bool = True) -> str:
    lines: list[str] = []

    if not result.ok():
        lines.append(_c(_RED, f"\u2718 {result.error}", color=color))
        return "\n".join(lines)

    lines.append(_c(_BOLD, result.summary(), color=color))
    lines.append("")

    for group_key, exprs in sorted(result.groups.items()):
        header = _c(_CYAN, f"[{group_key}]", color=color)
        lines.append(f"{header}  ({len(exprs)} expression(s))")
        for expr in exprs:
            lines.append(f"  {_c(_GREEN, expr, color=color)}")
        lines.append("")

    if result.ungrouped:
        lines.append(_c(_YELLOW, "[ungrouped / parse errors]", color=color))
        for expr in result.ungrouped:
            lines.append(f"  {expr}")
        lines.append("")

    return "\n".join(lines).rstrip()
