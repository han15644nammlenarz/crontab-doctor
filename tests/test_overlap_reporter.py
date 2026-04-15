"""Tests for overlap_reporter.py."""

import pytest

from crontab_doctor.overlap_reporter import OverlapReport, build_overlap_report
from crontab_doctor.conflict_detector import Conflict


# ---------------------------------------------------------------------------
# OverlapReport helpers
# ---------------------------------------------------------------------------

def test_overlap_report_no_conflicts_summary():
    report = OverlapReport(expressions=[], conflicts=[])
    assert report.summary() == "No overlapping schedules detected."
    assert not report.has_conflicts()


def test_overlap_report_with_error_summary():
    report = OverlapReport(expressions=[], error="bad expression")
    assert "bad expression" in report.summary()


def test_overlap_report_has_conflicts_true():
    c = Conflict(expression_a="* * * * *", expression_b="*/5 * * * *", reason="")
    report = OverlapReport(expressions=[], conflicts=[c])
    assert report.has_conflicts()


def test_overlap_report_summary_lists_pairs():
    c = Conflict(expression_a="0 * * * *", expression_b="0 12 * * *", reason="")
    report = OverlapReport(expressions=[], conflicts=[c])
    summary = report.summary()
    assert "0 * * * *" in summary
    assert "0 12 * * *" in summary


def test_overlap_report_summary_noun_singular():
    c = Conflict(expression_a="0 * * * *", expression_b="0 12 * * *", reason="")
    report = OverlapReport(expressions=[], conflicts=[c])
    assert "1 schedule overlap detected" in report.summary()


def test_overlap_report_summary_noun_plural():
    c1 = Conflict(expression_a="* * * * *", expression_b="0 * * * *", reason="")
    c2 = Conflict(expression_a="* * * * *", expression_b="0 12 * * *", reason="")
    report = OverlapReport(expressions=[], conflicts=[c1, c2])
    assert "2 schedule overlaps detected" in report.summary()


# ---------------------------------------------------------------------------
# build_overlap_report
# ---------------------------------------------------------------------------

def test_build_overlap_report_invalid_expression_returns_error():
    report = build_overlap_report(["not-valid", "* * * * *"])
    assert report.error != ""
    assert report.expressions == []


def test_build_overlap_report_no_overlap():
    # First-of-month vs 15th-of-month — no overlap
    report = build_overlap_report(["0 9 1 * *", "0 9 15 * *"])
    assert not report.error
    assert not report.has_conflicts()


def test_build_overlap_report_detects_overlap():
    # Both run every minute — definite overlap
    report = build_overlap_report(["* * * * *", "* * * * *"])
    assert not report.error
    assert report.has_conflicts()


def test_build_overlap_report_parses_all_expressions():
    report = build_overlap_report(["0 8 * * 1", "0 8 * * 2", "0 8 * * 3"])
    assert len(report.expressions) == 3
