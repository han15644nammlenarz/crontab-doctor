"""Format SearchResult objects for CLI output."""
from __future__ import annotations

from .cron_search import SearchResult

_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_CYAN = "\033[36m"


def _c(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}"


def format_search_result(result: SearchResult, *, color: bool = True) -> str:
    lines: list[str] = []

    header = f"Search: {result.query}"
    lines.append(_c(_BOLD, header) if color else header)
    lines.append("")

    if result.error:
        msg = f"  Error: {result.error}"
        lines.append(_c(_RED, msg) if color else msg)
        return "\n".join(lines)

    if not result.matches:
        msg = "  No matches found."
        lines.append(_c(_YELLOW, msg) if color else msg)
    else:
        count_line = f"  {len(result.matches)} match(es):"
        lines.append(_c(_GREEN, count_line) if color else count_line)
        for expr in result.matches:
            entry = f"    • {expr}"
            lines.append(_c(_CYAN, entry) if color else entry)

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)
