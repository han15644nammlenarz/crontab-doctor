"""Compute similarity scores between cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .conflict_detector import _expand_field
from .parser import ParseError, parse_expression


@dataclass
class SimilarityResult:
    left: str
    right: str
    score: float  # 0.0 – 1.0
    field_scores: List[float] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if not self.ok:
            return f"Error: {self.error}"
        pct = int(self.score * 100)
        label = _similarity_label(self.score)
        return (
            f"Similarity between '{self.left}' and '{self.right}': "
            f"{pct}% ({label})"
        )


def _similarity_label(score: float) -> str:
    if score >= 0.9:
        return "nearly identical"
    if score >= 0.7:
        return "very similar"
    if score >= 0.5:
        return "moderately similar"
    if score >= 0.25:
        return "slightly similar"
    return "dissimilar"


def _field_similarity(a_vals: set, b_vals: set) -> float:
    if not a_vals and not b_vals:
        return 1.0
    if not a_vals or not b_vals:
        return 0.0
    intersection = len(a_vals & b_vals)
    union = len(a_vals | b_vals)
    return intersection / union if union else 1.0


FIELD_NAMES = ("minute", "hour", "dom", "month", "dow")
FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "dom": (1, 31),
    "month": (1, 12),
    "dow": (0, 6),
}


def compare_expressions(left: str, right: str) -> SimilarityResult:
    """Return a SimilarityResult comparing *left* and *right*."""
    try:
        expr_l = parse_expression(left)
    except ParseError as exc:
        return SimilarityResult(left, right, 0.0, error=f"Left expression: {exc}")
    try:
        expr_r = parse_expression(right)
    except ParseError as exc:
        return SimilarityResult(left, right, 0.0, error=f"Right expression: {exc}")

    fields_l = [expr_l.minute, expr_l.hour, expr_l.dom, expr_l.month, expr_l.dow]
    fields_r = [expr_r.minute, expr_r.hour, expr_r.dom, expr_r.month, expr_r.dow]

    field_scores: List[float] = []
    for name, fl, fr in zip(FIELD_NAMES, fields_l, fields_r):
        lo, hi = FIELD_RANGES[name]
        vals_l = _expand_field(fl, lo, hi)
        vals_r = _expand_field(fr, lo, hi)
        field_scores.append(_field_similarity(set(vals_l), set(vals_r)))

    overall = sum(field_scores) / len(field_scores)
    return SimilarityResult(left, right, round(overall, 4), field_scores)
