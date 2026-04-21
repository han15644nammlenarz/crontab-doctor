"""Formatter for ExpressionDiff results."""
from __future__ import annotations

from .expression_diff import ExpressionDiff


def _c(text: str, code: str) -> str:
    """Wrap text in ANSI colour code."""
    return f"\033[{code}m{text}\033[0m"


def format_expression_diff(result: ExpressionDiff, *, color: bool = True) -> str:
    """Return a human-readable, optionally coloured diff report."""
    lines: list[str] = []

    def red(t: str) -> str:
        return _c(t, "31") if color else t

    def green(t: str) -> str:
        return _c(t, "32") if color else t

    def bold(t: str) -> str:
        return _c(t, "1") if color else t

    def yellow(t: str) -> str:
        return _c(t, "33") if color else t

    lines.append(bold("Expression Diff"))
    lines.append(f"  Left : {result.left}")
    lines.append(f"  Right: {result.right}")
    lines.append("")

    if result.error:
        lines.append(red(f"✗ {result.error}"))
        return "\n".join(lines)

    if result.identical:
        lines.append(green("✓ Expressions are identical."))
        return "\n".join(lines)

    lines.append(yellow(f"~ {len(result.field_diffs)} field(s) differ:"))
    for d in result.field_diffs:
        lines.append(
            f"  {bold(d.field_name):20s}  "
            f"{red(d.left):30s}  →  {green(d.right)}"
        )

    return "\n".join(lines)
