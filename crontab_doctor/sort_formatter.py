"""Format SortResult for CLI output."""
from __future__ import annotations

from .cron_sorter import SortResult, SortEntry


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _format_entry(entry: SortEntry, use_color: bool = True) -> str:
    rank_str = f"[{entry.rank:>2}]"
    if entry.error:
        label_part = f" ({entry.label})" if entry.label else ""
        expr_str = f"{entry.expression}{label_part}"
        error_str = f" !! {entry.error}"
        if use_color:
            return _c(rank_str, "2") + " " + _c(expr_str, "33") + _c(error_str, "31")
        return f"{rank_str} {expr_str}{error_str}"

    label_part = f"  ({entry.label})" if entry.label else ""
    key_part = f"  [{entry.sort_key}]" if entry.sort_key else ""
    line = f"{rank_str} {entry.expression}{label_part}{key_part}"
    if use_color:
        return _c(rank_str, "36") + " " + _c(entry.expression, "1") + _c(label_part, "2") + _c(key_part, "2")
    return line


def format_sort_result(result: SortResult, use_color: bool = True) -> str:
    lines: list[str] = []

    if not result.ok():
        msg = f"Error: {result.error}"
        lines.append(_c(msg, "31") if use_color else msg)
        return "\n".join(lines)

    header = f"Sorted by: {result.sort_by}  ({len(result.entries)} expression(s))"
    lines.append(_c(header, "1") if use_color else header)
    lines.append("")

    for entry in result.entries:
        lines.append(_format_entry(entry, use_color=use_color))

    lines.append("")
    summary = result.summary()
    lines.append(_c(summary, "2") if use_color else summary)
    return "\n".join(lines)
