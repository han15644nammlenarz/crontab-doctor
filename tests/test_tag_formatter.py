"""Tests for crontab_doctor.tag_formatter."""
from crontab_doctor.tag_manager import TagEntry
from crontab_doctor.tag_formatter import (
    format_tag_entry,
    format_tag_list,
    format_tag_summary,
)


def _entry(expr="0 9 * * 1-5", tags=None, note=None):
    return TagEntry(expression=expr, tags=tags or [], note=note)


def test_format_entry_contains_expression():
    result = format_tag_entry(_entry(), color=False)
    assert "0 9 * * 1-5" in result


def test_format_entry_contains_tags():
    result = format_tag_entry(_entry(tags=["work", "daily"]), color=False)
    assert "#work" in result
    assert "#daily" in result


def test_format_entry_no_tags_placeholder():
    result = format_tag_entry(_entry(), color=False)
    assert "(no tags)" in result


def test_format_entry_with_note():
    result = format_tag_entry(_entry(note="morning job"), color=False)
    assert "morning job" in result


def test_format_entry_without_note_no_dash():
    result = format_tag_entry(_entry(), color=False)
    assert "\u2014" not in result


def test_format_list_empty():
    result = format_tag_list([], color=False)
    assert "No tagged" in result


def test_format_list_contains_header():
    result = format_tag_list([_entry(tags=["x"])], color=False)
    assert "Tagged expressions" in result


def test_format_list_contains_each_entry():
    entries = [
        _entry("0 9 * * 1-5", tags=["work"]),
        _entry("*/15 * * * *", tags=["monitor"]),
    ]
    result = format_tag_list(entries, color=False)
    assert "0 9 * * 1-5" in result
    assert "*/15 * * * *" in result


def test_format_summary_counts():
    entries = [
        _entry(tags=["a", "b"]),
        _entry("*/5 * * * *", tags=["a"]),
    ]
    result = format_tag_summary(entries, color=False)
    assert "2 expression(s)" in result
    assert "2 unique tag(s)" in result


def test_format_summary_empty():
    result = format_tag_summary([], color=False)
    assert "0 expression(s)" in result
    assert "0 unique tag(s)" in result


def test_format_entry_color_mode_does_not_raise():
    entry = _entry(tags=["ci"], note="pipeline")
    result = format_tag_entry(entry, color=True)
    assert "0 9 * * 1-5" in result
