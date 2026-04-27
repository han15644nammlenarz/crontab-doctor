"""Tests for crontab_doctor.cron_pauser."""
import os
from datetime import datetime, timedelta, timezone

import pytest

from crontab_doctor.cron_pauser import (
    PauseEntry,
    is_paused,
    list_paused,
    pause_expression,
    resume_expression,
)


@pytest.fixture()
def pause_file(tmp_path):
    return str(tmp_path / "paused.json")


def test_pause_creates_entry(pause_file):
    entry = pause_expression("0 * * * *", reason="maintenance", path=pause_file)
    assert entry.expression == "0 * * * *"
    assert entry.reason == "maintenance"
    assert entry.resume_at is None


def test_pause_entry_repr():
    e = PauseEntry(expression="* * * * *", reason="testing", paused_at="2024-01-01T00:00:00+00:00")
    assert "* * * * *" in repr(e)
    assert "testing" in repr(e)


def test_is_paused_returns_true_after_pause(pause_file):
    pause_expression("5 4 * * *", path=pause_file)
    assert is_paused("5 4 * * *", path=pause_file) is True


def test_is_paused_returns_false_for_unknown(pause_file):
    assert is_paused("1 2 3 4 5", path=pause_file) is False


def test_resume_removes_entry(pause_file):
    pause_expression("0 0 * * *", path=pause_file)
    result = resume_expression("0 0 * * *", path=pause_file)
    assert result is True
    assert is_paused("0 0 * * *", path=pause_file) is False


def test_resume_nonexistent_returns_false(pause_file):
    result = resume_expression("9 9 9 9 9", path=pause_file)
    assert result is False


def test_list_paused_empty(pause_file):
    entries = list_paused(path=pause_file)
    assert entries == []


def test_list_paused_multiple(pause_file):
    pause_expression("0 1 * * *", reason="r1", path=pause_file)
    pause_expression("0 2 * * *", reason="r2", path=pause_file)
    entries = list_paused(path=pause_file)
    expressions = [e.expression for e in entries]
    assert "0 1 * * *" in expressions
    assert "0 2 * * *" in expressions


def test_pause_with_resume_at(pause_file):
    future = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    entry = pause_expression("* * * * *", resume_at=future, path=pause_file)
    assert entry.resume_at == future
    assert is_paused("* * * * *", path=pause_file) is True


def test_expired_pause_auto_resumes(pause_file):
    past = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    pause_expression("0 6 * * *", resume_at=past, path=pause_file)
    # is_paused should detect expiry and auto-resume
    assert is_paused("0 6 * * *", path=pause_file) is False


def test_is_expired_false_when_no_resume_at():
    e = PauseEntry(expression="x", reason="", paused_at="2024-01-01T00:00:00+00:00")
    assert e.is_expired() is False


def test_pause_entry_from_dict_roundtrip():
    original = PauseEntry(
        expression="30 8 * * 1",
        reason="weekly",
        paused_at="2024-06-01T08:00:00+00:00",
        resume_at="2024-06-08T08:00:00+00:00",
    )
    restored = PauseEntry.from_dict(original.to_dict())
    assert restored.expression == original.expression
    assert restored.reason == original.reason
    assert restored.resume_at == original.resume_at
