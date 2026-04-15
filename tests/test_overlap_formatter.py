"""Tests for overlap_formatter.py."""

import pytest

from crontab_doctor.overlap_reporter import OverlapReport
from crontab_doctor.conflict_detector import Conflict
from crontab_doctor.overlap_formatter import format_overlap_report


def _report_no_conflicts(n=2):
    from crontab_doctor.parser import parse_expression
    exprs = [parse_expression("0 8 * * 1"), parse_expression("0 9 * * 2")]
    return OverlapReport(expressions=exprs[:n], conflicts=[])


def test_format_no_conflicts_contains_checkmark():
    out = format_overlap_report(_report_no_conflicts(), color=False)
    assert "✔" in out


def test_format_no_conflicts_mentions_expression_count():
    out = format_overlap_report(_report_no_conflicts(), color=False)
    assert "2 expression" in out


def test_format_with_conflicts_contains_warning():
    c = Conflict(expression_a="* * * * *", expression_b="*/5 * * * *", reason="")
    from crontab_doctor.parser import parse_expression
    report = OverlapReport(
        expressions=[parse_expression("* * * * *"), parse_expression("*/5 * * * *")],
        conflicts=[c],
    )
    out = format_overlap_report(report, color=False)
    assert "⚠" in out


def test_format_with_conflicts_lists_expressions():
    c = Conflict(expression_a="* * * * *", expression_b="*/5 * * * *", reason="overlap")
    from crontab_doctor.parser import parse_expression
    report = OverlapReport(
        expressions=[parse_expression("* * * * *"), parse_expression("*/5 * * * *")],
        conflicts=[c],
    )
    out = format_overlap_report(report, color=False)
    assert "* * * * *" in out
    assert "overlap" in out


def test_format_error_report():
    report = OverlapReport(expressions=[], error="ParseError: bad token")
    out = format_overlap_report(report, color=False)
    assert "ERROR" in out
    assert "ParseError" in out


def test_format_color_flag_does_not_crash():
    report = _report_no_conflicts()
    out_color = format_overlap_report(report, color=True)
    out_plain = format_overlap_report(report, color=False)
    # Both should contain the key info
    assert "✔" in out_color
    assert "✔" in out_plain
