"""Tests for crontab_doctor.schedule_diff."""

import pytest
from unittest.mock import patch
from datetime import datetime

from crontab_doctor.schedule_diff import diff_expressions, ScheduleDiff


BASE_NOW = datetime(2024, 1, 15, 12, 0, 0)


def _make_dts(minutes):
    """Return datetime objects at fixed hour, varying minutes."""
    return [datetime(2024, 1, 15, 12, m, 0) for m in minutes]


def test_diff_identical_expressions_all_shared():
    diff = diff_expressions("*/5 * * * *", "*/5 * * * *", count=10)
    assert diff.error == ""
    assert len(diff.shared) > 0
    assert diff.only_in_a == []
    assert diff.only_in_b == []


def test_diff_disjoint_expressions():
    # One runs at minute 1, the other at minute 3 — unlikely to overlap in 5 samples
    with patch("crontab_doctor.schedule_diff.next_runs") as mock_nr:
        mock_nr.side_effect = [
            _make_dts([1, 11, 21, 31, 41]),
            _make_dts([3, 13, 23, 33, 43]),
        ]
        diff = diff_expressions("1 * * * *", "3 * * * *", count=5)

    assert diff.error == ""
    assert diff.shared == []
    assert len(diff.only_in_a) == 5
    assert len(diff.only_in_b) == 5


def test_diff_partial_overlap():
    with patch("crontab_doctor.schedule_diff.next_runs") as mock_nr:
        mock_nr.side_effect = [
            _make_dts([0, 10, 20, 30]),
            _make_dts([0, 15, 30, 45]),
        ]
        diff = diff_expressions("*/10 * * * *", "*/15 * * * *", count=4)

    assert diff.error == ""
    shared_minutes = {int(t.split(":")[1]) for t in diff.shared}
    assert shared_minutes == {0, 30}
    assert len(diff.only_in_a) == 2  # 10, 20
    assert len(diff.only_in_b) == 2  # 15, 45


def test_diff_invalid_first_expression():
    diff = diff_expressions("99 99 99 99 99", "* * * * *", count=5)
    assert diff.error != ""
    assert "first" in diff.error.lower() or "invalid" in diff.error.lower()


def test_diff_invalid_second_expression():
    diff = diff_expressions("* * * * *", "bad expression", count=5)
    assert diff.error != ""
    assert "second" in diff.error.lower() or "invalid" in diff.error.lower()


def test_summary_contains_expressions():
    with patch("crontab_doctor.schedule_diff.next_runs") as mock_nr:
        mock_nr.side_effect = [_make_dts([0, 30]), _make_dts([0, 30])]
        diff = diff_expressions("0 * * * *", "30 * * * *", count=2)

    summary = diff.summary()
    assert "0 * * * *" in summary
    assert "30 * * * *" in summary


def test_summary_on_error():
    diff = ScheduleDiff(expr_a="bad", expr_b="* * * * *", error="Invalid first expression: oops")
    assert "Error" in diff.summary()
    assert "oops" in diff.summary()


def test_diff_returns_schedule_diff_type():
    diff = diff_expressions("* * * * *", "* * * * *", count=5)
    assert isinstance(diff, ScheduleDiff)
