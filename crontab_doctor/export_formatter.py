"""Format ExportResult objects for CLI display."""
from __future__ import annotations

import sys

from .cron_exporter import ExportResult

_USE_COLOR = sys.stdout.isatty()


def _c(text: str, code: str) -> str:
    if not _USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def format_export_result(result: ExportResult) -> str:
    lines: list[str] = []

    header = _c("Export Result", "1")
    lines.append(header)
    lines.append(_c("-" * 40, "2"))

    expr_label = _c("Expression:", "36")
    lines.append(f"{expr_label} {result.expression}")

    fmt_label = _c("Format:", "36")
    lines.append(f"{fmt_label} {result.format}")

    if result.label:
        lbl = _c("Label:", "36")
        lines.append(f"{lbl} {result.label}")

    if result.tags:
        tags_label = _c("Tags:", "36")
        lines.append(f"{tags_label} {', '.join(result.tags)}")

    lines.append("")

    if not result.ok():
        err = _c(f"✗ Error: {result.error}", "31")
        lines.append(err)
        return "\n".join(lines)

    status = _c("✓ " + result.summary(), "32")
    lines.append(status)
    lines.append("")

    if result.output:
        output_label = _c("Output:", "33")
        lines.append(output_label)
        lines.append(result.output)

    return "\n".join(lines)
