"""Format LabelEntry objects for CLI display."""
from __future__ import annotations

from typing import List

from crontab_doctor.label_manager import LabelEntry


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_label_entry(entry: LabelEntry, *, color: bool = True) -> str:
    lines: List[str] = []
    expr = _c("36", entry.expression) if color else entry.expression
    lbl = _c("1", entry.label) if color else entry.label
    lines.append(f"{expr}  →  {lbl}")
    if entry.description:
        lines.append(f"  {entry.description}")
    if entry.tags:
        tag_str = ", ".join(entry.tags)
        tag_line = f"  tags: {_c('33', tag_str)}" if color else f"  tags: {tag_str}"
        lines.append(tag_line)
    return "\n".join(lines)


def format_label_list(entries: List[LabelEntry], *, color: bool = True) -> str:
    if not entries:
        return "No labels defined."
    blocks = [format_label_entry(e, color=color) for e in entries]
    return "\n\n".join(blocks)


def format_label_summary(entries: List[LabelEntry], *, color: bool = True) -> str:
    n = len(entries)
    noun = "label" if n == 1 else "labels"
    header = _c("1;32", f"{n} {noun} stored.") if color else f"{n} {noun} stored."
    return header
