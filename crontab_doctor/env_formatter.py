"""Formatter for EnvCheckResult objects."""
from __future__ import annotations

from typing import List

from crontab_doctor.env_checker import EnvCheckResult

_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"


def _c(text: str, code: str, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_env_result(result: EnvCheckResult, color: bool = True) -> str:
    lines: List[str] = []
    lines.append(f"Expression : {result.expression}")
    if result.command:
        lines.append(f"Command    : {result.command}")

    if not result.referenced:
        lines.append(_c("  No environment variables referenced.", _GREEN, color))
        return "\n".join(lines)

    lines.append("  Referenced variables:")
    for var in result.referenced:
        if var in result.defined:
            lines.append("    " + _c(f"✔ {var} (defined)", _GREEN, color))
        else:
            lines.append("    " + _c(f"✘ {var} (MISSING)", _RED, color))

    if result.ok:
        lines.append(_c("  All environment variables are defined.", _GREEN, color))
    else:
        missing_str = ", ".join(result.missing)
        lines.append(
            _c(f"  WARNING: missing variable(s): {missing_str}", _YELLOW, color)
        )
    return "\n".join(lines)


def format_env_results(results: List[EnvCheckResult], color: bool = True) -> str:
    sections = [format_env_result(r, color=color) for r in results]
    separator = "\n" + "-" * 50 + "\n"
    return separator.join(sections)
