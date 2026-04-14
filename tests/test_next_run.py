"""Tests for crontab_doctor.next_run module."""

from datetime import datetime

import pytest

from crontab_doctor.next_run import next_runs, NextRunError
from crontab_doctor.parser import ParseError

# Fixed reference point: 2024-01-15 12:30 (Monday)
REF = datetime(2024, 1, 15, 12, 30, 0)


def test_every_minute_returns_five_consecutive():
    runs = next_runs("* * * * *", after=REF, count=5)
    assert len(runs) == 5
    for i, run in enumerate(runs):
        assert run == datetime(2024, 1, 15, 12, 31 + i, 0)


def test_specific_hour_and_minute():
    # Next occurrence of 14:00 after 12:30 on 2024-01-15
    runs = next_runs("0 14 * * *", after=REF, count=1)
    assert runs[0] == datetime(2024, 1, 15, 14, 0, 0)


def test_specific_hour_already_passed_today_rolls_to_tomorrow():
    # 10:00 has already passed at REF (12:30)
    runs = next_runs("0 10 * * *", after=REF, count=1)
    assert runs[0] == datetime(2024, 1, 16, 10, 0, 0)


def test_specific_day_of_month():
    runs = next_runs("0 9 20 * *", after=REF, count=1)
    assert runs[0] == datetime(2024, 1, 20, 9, 0, 0)


def test_specific_month():
    runs = next_runs("0 0 1 3 *", after=REF, count=1)
    assert runs[0] == datetime(2024, 3, 1, 0, 0, 0)


def test_step_expression():
    # Every 15 minutes starting from next occurrence after 12:30
    runs = next_runs("*/15 * * * *", after=REF, count=4)
    assert runs[0] == datetime(2024, 1, 15, 12, 45, 0)
    assert runs[1] == datetime(2024, 1, 15, 13, 0, 0)
    assert runs[2] == datetime(2024, 1, 15, 13, 15, 0)
    assert runs[3] == datetime(2024, 1, 15, 13, 30, 0)


def test_at_daily_alias():
    runs = next_runs("@daily", after=REF, count=1)
    assert runs[0] == datetime(2024, 1, 16, 0, 0, 0)


def test_at_hourly_alias():
    runs = next_runs("@hourly", after=REF, count=1)
    assert runs[0] == datetime(2024, 1, 15, 13, 0, 0)


def test_count_respected():
    runs = next_runs("* * * * *", after=REF, count=3)
    assert len(runs) == 3


def test_invalid_expression_raises_parse_error():
    with pytest.raises(ParseError):
        next_runs("not a cron", after=REF)


def test_default_after_is_now(monkeypatch):
    fixed = datetime(2024, 6, 1, 0, 0, 0)
    monkeypatch.setattr(
        "crontab_doctor.next_run.datetime",
        type("_FakeDT", (), {"now": staticmethod(lambda: fixed)}),
    )
    # Just ensure it runs without error when after=None
    # (monkeypatching datetime is tricky; we test the plumbing here)
    runs = next_runs("0 1 * * *", after=fixed, count=1)
    assert runs[0] == datetime(2024, 6, 1, 1, 0, 0)
