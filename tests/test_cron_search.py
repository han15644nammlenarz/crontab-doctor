"""Tests for cron_search and search_formatter."""
import pytest

from crontab_doctor.cron_search import search_expressions, SearchResult
from crontab_doctor.search_formatter import format_search_result

EXPRESSIONS = [
    "* * * * *",
    "0 * * * *",
    "0 0 * * *",
    "0 0 1 * *",
    "30 6 * * 1",
    "*/5 * * * *",
    "0 12 * * MON",
]


# --- SearchResult unit tests ---

def test_search_result_ok_when_no_error():
    r = SearchResult(query="test", matches=["* * * * *"])
    assert r.ok() is True


def test_search_result_not_ok_when_error():
    r = SearchResult(query="", error="Query must not be empty.")
    assert r.ok() is False


def test_search_result_summary_no_matches():
    r = SearchResult(query="foo", matches=[])
    assert "0 matches" in r.summary()


def test_search_result_summary_singular():
    r = SearchResult(query="foo", matches=["* * * * *"])
    assert "1 match" in r.summary()
    assert "matches" not in r.summary()


def test_search_result_summary_plural():
    r = SearchResult(query="0", matches=["0 * * * *", "0 0 * * *"])
    assert "2 matches" in r.summary()


def test_search_result_summary_error():
    r = SearchResult(query="", error="bad query")
    assert "error" in r.summary().lower()


# --- search_expressions tests ---

def test_empty_query_returns_error():
    result = search_expressions(EXPRESSIONS, "")
    assert not result.ok()
    assert result.error


def test_full_text_search_finds_matches():
    result = search_expressions(EXPRESSIONS, "*/5")
    assert result.ok()
    assert "*/5 * * * *" in result.matches


def test_full_text_search_no_match():
    result = search_expressions(EXPRESSIONS, "99")
    assert result.ok()
    assert result.matches == []


def test_field_search_minute_zero():
    result = search_expressions(EXPRESSIONS, "0", field_index=0)
    assert result.ok()
    # "0 * * * *", "0 0 * * *", "0 0 1 * *", "0 12 * * MON" have '0' in minute
    for expr in result.matches:
        assert expr.split()[0] == "0" or "0" in expr.split()[0]


def test_field_search_hour_twelve():
    result = search_expressions(EXPRESSIONS, "12", field_index=1)
    assert result.ok()
    assert "0 12 * * MON" in result.matches


def test_field_search_dow_mon():
    result = search_expressions(EXPRESSIONS, "MON", field_index=4)
    assert result.ok()
    assert "0 12 * * MON" in result.matches


def test_field_index_out_of_range_returns_no_matches():
    result = search_expressions(EXPRESSIONS, "*", field_index=9)
    assert result.ok()
    assert result.matches == []


# --- format_search_result tests ---

def test_format_contains_query():
    result = search_expressions(EXPRESSIONS, "*/5")
    output = format_search_result(result, color=False)
    assert "*/5" in output


def test_format_shows_matches():
    result = search_expressions(EXPRESSIONS, "*/5")
    output = format_search_result(result, color=False)
    assert "*/5 * * * *" in output


def test_format_no_matches_message():
    result = search_expressions(EXPRESSIONS, "99")
    output = format_search_result(result, color=False)
    assert "No matches" in output


def test_format_error_message():
    result = search_expressions(EXPRESSIONS, "")
    output = format_search_result(result, color=False)
    assert "Error" in output


def test_format_with_color_does_not_crash():
    result = search_expressions(EXPRESSIONS, "0")
    output = format_search_result(result, color=True)
    assert "0" in output
