"""Formatting helpers for tag manager output."""
from __future__ import annotations

from typing import List

from crontab_doctor.formatter import _colorize
from crontab_doctor.tag_manager import TagEntry


def format_tag_entry(entry: TagEntry, *, color: bool = True) -> str:
    """Return a single-line human-readable representation of a TagEntry."""
    expr = _colorize(entry.expression, "cyan") if color else entry.expression
    if entry.tags:
        tag_str = " ".join(
            (_colorize(f"#{t}", "yellow") if color else f"#{t}")
            for t in entry.tags
        )
    else:
        tag_str = _colorize("(no tags)", "white") if color else "(no tags)"
    parts = [expr, tag_str]
    if entry.note:
        note = _colorize(f"— {entry.note}", "white") if color else f"— {entry.note}"
        parts.append(note)
    return "  ".join(parts)


def format_tag_list(entries: List[TagEntry], *, color: bool = True) -> str:
    """Return a formatted multi-line block for a list of TagEntry objects."""
    if not entries:
        msg = "No tagged expressions found."
        return _colorize(msg, "white") if color else msg
    header = _colorize("Tagged expressions:", "green") if color else "Tagged expressions:"
    lines = [header]
    for entry in entries:
        lines.append("  " + format_tag_entry(entry, color=color))
    return "\n".join(lines)


def format_tag_summary(entries: List[TagEntry], *, color: bool = True) -> str:
    """Return a summary line counting tags and expressions."""
    tag_set: set = set()
    for e in entries:
        tag_set.update(e.tags)
    summary = (
        f"{len(entries)} expression(s) tagged across "
        f"{len(tag_set)} unique tag(s)."
    )
    return _colorize(summary, "cyan") if color else summary
