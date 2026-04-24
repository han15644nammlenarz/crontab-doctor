"""Formatter for SimilarityResult objects."""
from __future__ import annotations

from typing import List

from .cron_similarity import FIELD_NAMES, SimilarityResult


def _c(code: str, text: str) -> str:
    """Wrap *text* in an ANSI colour escape."""
    return f"\033[{code}m{text}\033[0m"


def _bar(score: float, width: int = 20) -> str:
    filled = round(score * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _score_color(score: float) -> str:
    if score >= 0.7:
        return "32"  # green
    if score >= 0.4:
        return "33"  # yellow
    return "31"  # red


def format_similarity(result: SimilarityResult, *, color: bool = True) -> str:
    lines: List[str] = []

    if not result.ok:
        msg = f"✗ {result.error}"
        lines.append(_c("31", msg) if color else msg)
        return "\n".join(lines)

    header = f"Similarity: '{result.left}'  vs  '{result.right}'"
    lines.append(_c("1", header) if color else header)
    lines.append("")

    for name, score in zip(FIELD_NAMES, result.field_scores):
        bar = _bar(score)
        pct = f"{int(score * 100):3d}%"
        col = _score_color(score)
        score_str = _c(col, f"{pct} {bar}") if color else f"{pct} {bar}"
        lines.append(f"  {name:<8} {score_str}")

    lines.append("")
    overall_pct = int(result.score * 100)
    col = _score_color(result.score)
    overall_str = _c(col, f"{overall_pct}%") if color else f"{overall_pct}%"
    lines.append(f"  Overall:  {overall_str}  — {result.summary().split(': ', 1)[-1]}")

    return "\n".join(lines)


def format_similarity_list(
    results: List[SimilarityResult], *, color: bool = True
) -> str:
    if not results:
        return "No comparisons to display."
    return "\n\n".join(format_similarity(r, color=color) for r in results)
