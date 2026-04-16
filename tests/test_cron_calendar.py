"""Tests for cron_calendar and calendar_formatter."""
from datetime import datetime
import pytest
from crontab_doctor.cron_calendar import build_calendar, CalendarEntry, CalendarResult
from crontab_doctor.calendar_formatter import format_calendar

SINCE = datetime(2024, 6, 1, 12, 0)


def test_build_calendar_every_minute_returns_entries():
    result = build_calendar(["* * * * *"], since=SINCE, count=5, window_hours=1)
    assert result.ok
    assert len(result.entries) == 1
    assert len(result.entries[0].runs) == 5


def test_build_calendar_respects_window():
    # specific minute far in future should yield 0 runs in 1-hour window
    result = build_calendar(["59 23 * * *"], since=SINCE, count=5, window_hours=1)
    assert result.ok
    assert result.entries[0].runs == []


def test_build_calendar_multiple_expressions():
    result = build_calendar(["* * * * *", "0 * * * *"], since=SINCE, count=3, window_hours=2)
    assert result.ok
    assert len(result.entries) == 2


def test_build_calendar_assigns_labels():
    result = build_calendar(["* * * * *"], labels=["my-job"], since=SINCE, count=2)
    assert result.entries[0].label == "my-job"


def test_build_calendar_no_labels_defaults_none():
    result = build_calendar(["* * * * *"], since=SINCE, count=2)
    assert result.entries[0].label is None


def test_build_calendar_invalid_expression_returns_error():
    result = build_calendar(["invalid expr"], since=SINCE, count=2)
    assert not result.ok
    assert result.error


def test_calendar_result_summary_ok():
    result = build_calendar(["* * * * *"], since=SINCE, count=3, window_hours=1)
    s = result.summary()
    assert "1 expression" in s


def test_calendar_result_to_dict():
    entry = CalendarEntry(expression="* * * * *", label="j", runs=[SINCE])
    d = entry.to_dict()
    assert d["expression"] == "* * * * *"
    assert d["label"] == "j"
    assert isinstance(d["runs"], list)


def test_format_calendar_no_color_contains_expression():
    result = build_calendar(["* * * * *"], since=SINCE, count=2, window_hours=1)
    out = format_calendar(result, color=False)
    assert "* * * * *" in out


def test_format_calendar_error_shows_message():
    result = CalendarResult(error="something went wrong")
    out = format_calendar(result, color=False)
    assert "something went wrong" in out


def test_format_calendar_no_runs_in_window():
    result = build_calendar(["59 23 31 12 *"], since=SINCE, count=5, window_hours=1)
    out = format_calendar(result, color=False)
    assert "No runs in window" in out


def test_format_calendar_with_label_shows_label():
    result = build_calendar(["* * * * *"], labels=["backup-job"], since=SINCE, count=2, window_hours=1)
    out = format_calendar(result, color=False)
    assert "backup-job" in out
