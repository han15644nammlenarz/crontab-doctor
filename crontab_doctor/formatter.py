"""Formatter module for crontab-doctor.

Provides human-readable output formatting for audit results,
conflicts, and validation errors.
"""

from typing import List
from crontab_doctor.auditor import AuditResult
from crontab_doctor.conflict_detector import Conflict


ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_GREEN = "\033[92m"
ANSI_CYAN = "\033[96m"
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_audit_result(result: AuditResult, use_color: bool = True) -> str:
    """Format a single AuditResult into a human-readable string."""
    lines = []
    header = _colorize(f"Expression: {result.expression}", ANSI_BOLD, use_color)
    lines.append(header)

    if result.explanation:
        lines.append(f"  Schedule : {result.explanation}")

    if result.errors:
        for err in result.errors:
            lines.append(_colorize(f"  ERROR     : {err}", ANSI_RED, use_color))
    else:
        lines.append(_colorize("  Status    : valid", ANSI_GREEN, use_color))

    if result.warnings:
        for warn in result.warnings:
            lines.append(_colorize(f"  WARNING   : {warn}", ANSI_YELLOW, use_color))

    return "\n".join(lines)


def format_conflicts(conflicts: List[Conflict], use_color: bool = True) -> str:
    """Format a list of Conflict objects into a human-readable string."""
    if not conflicts:
        return _colorize("No conflicts detected.", ANSI_GREEN, use_color)

    lines = [_colorize(f"Conflicts detected: {len(conflicts)}", ANSI_BOLD, use_color)]
    for i, conflict in enumerate(conflicts, start=1):
        lines.append(
            _colorize(f"  [{i}] ", ANSI_CYAN, use_color)
            + f"{conflict.expression_a!r} overlaps with {conflict.expression_b!r}"
        )
        lines.append(f"      Reason: {conflict.reason}")
    return "\n".join(lines)


def format_summary(results: List[AuditResult], use_color: bool = True) -> str:
    """Format a summary line for multiple audit results."""
    total = len(results)
    valid = sum(1 for r in results if not r.errors)
    invalid = total - valid
    warnings = sum(len(r.warnings) for r in results)

    parts = [
        _colorize(f"Total: {total}", ANSI_BOLD, use_color),
        _colorize(f"Valid: {valid}", ANSI_GREEN, use_color),
        _colorize(f"Invalid: {invalid}", ANSI_RED if invalid else ANSI_GREEN, use_color),
        _colorize(f"Warnings: {warnings}", ANSI_YELLOW if warnings else ANSI_GREEN, use_color),
    ]
    return "  ".join(parts)
