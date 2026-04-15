"""Formatter for OverlapReport objects."""

from .overlap_reporter import OverlapReport
from .formatter import _colorize


def format_overlap_report(report: OverlapReport, *, color: bool = True) -> str:
    """Return a human-readable string describing the overlap report."""
    lines: list[str] = []

    if report.error:
        msg = f"[ERROR] {report.error}"
        lines.append(_colorize(msg, "red") if color else msg)
        return "\n".join(lines)

    header = f"Checked {len(report.expressions)} expression(s) for overlaps."
    lines.append(_colorize(header, "cyan") if color else header)

    if not report.has_conflicts():
        ok = "  ✔ No overlapping schedules."
        lines.append(_colorize(ok, "green") if color else ok)
        return "\n".join(lines)

    warn = f"  ⚠  {len(report.conflicts)} overlap(s) found:"
    lines.append(_colorize(warn, "yellow") if color else warn)

    for conflict in report.conflicts:
        detail = f"    • {conflict.expression_a!r}  ⇄  {conflict.expression_b!r}"
        if conflict.reason:
            detail += f"  ({conflict.reason})"
        lines.append(detail)

    return "\n".join(lines)
