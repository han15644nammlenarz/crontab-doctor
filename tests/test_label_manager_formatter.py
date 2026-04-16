"""Tests for label_manager and label_formatter."""
import pytest
from pathlib import Path

from crontab_doctor.label_manager import (
    LabelEntry,
    set_label,
    get_label,
    list_labels,
    remove_label,
)
from crontab_doctor.label_formatter import (
    format_label_entry,
    format_label_list,
    format_label_summary,
)


@pytest.fixture
def labels_file(tmp_path):
    return tmp_path / "labels.json"


def test_set_and_get_label(labels_file):
    entry = set_label("0 * * * *", "Hourly job", path=labels_file)
    assert entry.label == "Hourly job"
    fetched = get_label("0 * * * *", path=labels_file)
    assert fetched is not None
    assert fetched.label == "Hourly job"


def test_get_missing_label_returns_none(labels_file):
    assert get_label("* * * * *", path=labels_file) is None


def test_set_label_with_description_and_tags(labels_file):
    set_label("0 0 * * *", "Daily", description="Runs at midnight", tags=["prod"], path=labels_file)
    e = get_label("0 0 * * *", path=labels_file)
    assert e.description == "Runs at midnight"
    assert "prod" in e.tags


def test_set_label_overwrites(labels_file):
    set_label("5 4 * * *", "Old label", path=labels_file)
    set_label("5 4 * * *", "New label", path=labels_file)
    assert get_label("5 4 * * *", path=labels_file).label == "New label"


def test_list_labels_empty(labels_file):
    assert list_labels(path=labels_file) == []


def test_list_labels_multiple(labels_file):
    set_label("* * * * *", "Every minute", path=labels_file)
    set_label("0 12 * * *", "Noon", path=labels_file)
    assert len(list_labels(path=labels_file)) == 2


def test_remove_label(labels_file):
    set_label("0 6 * * *", "Morning", path=labels_file)
    removed = remove_label("0 6 * * *", path=labels_file)
    assert removed is True
    assert get_label("0 6 * * *", path=labels_file) is None


def test_remove_missing_label_returns_false(labels_file):
    assert remove_label("1 1 1 1 1", path=labels_file) is False


def test_label_entry_repr():
    e = LabelEntry(expression="* * * * *", label="All stars")
    assert "All stars" in repr(e)


def test_format_entry_contains_expression():
    e = LabelEntry(expression="0 0 * * 0", label="Weekly")
    out = format_label_entry(e, color=False)
    assert "0 0 * * 0" in out
    assert "Weekly" in out


def test_format_entry_with_description():
    e = LabelEntry(expression="0 0 * * *", label="Daily", description="Midnight run")
    out = format_label_entry(e, color=False)
    assert "Midnight run" in out


def test_format_entry_with_tags():
    e = LabelEntry(expression="0 0 * * *", label="Daily", tags=["infra", "prod"])
    out = format_label_entry(e, color=False)
    assert "infra" in out
    assert "prod" in out


def test_format_list_empty():
    assert "No labels" in format_label_list([], color=False)


def test_format_summary_singular():
    e = LabelEntry(expression="* * * * *", label="x")
    out = format_label_summary([e], color=False)
    assert "1 label" in out


def test_format_summary_plural():
    entries = [LabelEntry(expression=str(i), label=f"l{i}") for i in range(3)]
    out = format_label_summary(entries, color=False)
    assert "3 labels" in out
