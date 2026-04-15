"""Formatting helpers for lint warnings."""

from typing import List

from .lint import LintWarning
from .formatter import _colorize


_SEVERITY_COLORS = {
    "warning": "yellow",
    "info": "cyan",
}

_SEVERITY_PREFIX = {
    "warning": "⚠ ",
    "info": "ℹ ",
}


def format_lint_warning(w: LintWarning, *, color: bool = True) -> str:
    """Return a single-line string representation of *w*."""
    prefix = _SEVERITY_PREFIX.get(w.severity, "")
    clr = _SEVERITY_COLORS.get(w.severity, "white")
    code_part = _colorize(f"[{w.code}]", clr) if color else f"[{w.code}]"
    return f"{prefix}{code_part} {w.message}"


def format_lint_results(
    raw: str,
    warnings: List[LintWarning],
    *,
    color: bool = True,
) -> str:
    """Return a multi-line formatted block for all lint results of *raw*."""
    lines: List[str] = []
    header = f"Lint results for: {raw}"
    lines.append(_colorize(header, "white") if color else header)
    lines.append("-" * min(len(header), 72))

    if not warnings:
        ok = "✔ No lint warnings."
        lines.append(_colorize(ok, "green") if color else ok)
    else:
        for w in warnings:
            lines.append(format_lint_warning(w, color=color))

    return "\n".join(lines)


def format_lint_summary(results: dict, *, color: bool = True) -> str:
    """Summarise lint results across multiple expressions.

    *results* maps raw expression string -> list[LintWarning].
    """
    total_warnings = sum(len(v) for v in results.values())
    total_exprs = len(results)
    lines = [
        _colorize("Lint Summary", "white") if color else "Lint Summary",
        f"  Expressions checked : {total_exprs}",
        f"  Total warnings      : {total_warnings}",
    ]
    return "\n".join(lines)
