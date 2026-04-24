"""Format AnomalyResult objects for CLI output."""
from __future__ import annotations

import sys

from .anomaly_detector import AnomalyResult, AnomalyWarning

_USE_COLOR = sys.stdout.isatty()

_SEVERITY_COLORS = {
    "info": "\033[36m",      # cyan
    "warning": "\033[33m",   # yellow
    "critical": "\033[31m",  # red
}
_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"


def _c(text: str, code: str) -> str:
    if not _USE_COLOR:
        return text
    return f"{code}{text}{_RESET}"


def _severity_prefix(severity: str) -> str:
    color = _SEVERITY_COLORS.get(severity, "")
    label = severity.upper()
    return _c(f"[{label}]", color)


def format_anomaly_warning(warning: AnomalyWarning) -> str:
    prefix = _severity_prefix(warning.severity)
    code = _c(warning.code, _BOLD)
    return f"  {prefix} {code}: {warning.message}"


def format_anomaly_result(result: AnomalyResult) -> str:
    lines: list[str] = []
    header = _c(result.expression, _BOLD)
    lines.append(f"Expression: {header}")

    if result.error:
        lines.append(_c(f"  [ERROR] {result.error}", _SEVERITY_COLORS["critical"]))
        return "\n".join(lines)

    if not result.warnings:
        lines.append(_c("  ✔ No anomalies detected.", _GREEN))
    else:
        lines.append(f"  {len(result.warnings)} anomaly warning(s):")
        for w in result.warnings:
            lines.append(format_anomaly_warning(w))

    return "\n".join(lines)


def format_anomaly_results(results: list[AnomalyResult]) -> str:
    sections = [format_anomaly_result(r) for r in results]
    total = len(results)
    flagged = sum(1 for r in results if r.warnings or not r.ok)
    summary = _c(
        f"\n{flagged}/{total} expression(s) have anomalies.",
        _BOLD,
    )
    sections.append(summary)
    return "\n\n".join(sections)
