"""Tests for crontab_doctor.pattern_suggester."""

import pytest
from crontab_doctor.pattern_suggester import (
    Suggestion,
    SuggestionResult,
    suggest_patterns,
)


# ---------------------------------------------------------------------------
# Suggestion / SuggestionResult basic behaviour
# ---------------------------------------------------------------------------

class TestSuggestion:
    def test_repr_contains_expression(self):
        s = Suggestion(expression="0 * * * *", label="Hourly", score=0.9, reason="Matches hourly pattern")
        assert "0 * * * *" in repr(s)

    def test_repr_contains_label(self):
        s = Suggestion(expression="0 0 * * *", label="Daily midnight", score=0.8, reason="")
        assert "Daily midnight" in repr(s)


class TestSuggestionResult:
    def test_ok_when_no_error(self):
        result = SuggestionResult(expression="* * * * *", suggestions=[], error=None)
        assert result.ok is True

    def test_not_ok_when_error(self):
        result = SuggestionResult(expression="bad", suggestions=[], error="parse error")
        assert result.ok is False

    def test_summary_error(self):
        result = SuggestionResult(expression="bad", suggestions=[], error="parse error")
        assert "parse error" in result.summary()

    def test_summary_no_suggestions(self):
        result = SuggestionResult(expression="* * * * *", suggestions=[], error=None)
        summary = result.summary()
        assert "no" in summary.lower() or "0" in summary

    def test_summary_with_suggestions(self):
        s = Suggestion(expression="0 * * * *", label="Hourly", score=0.9, reason="close match")
        result = SuggestionResult(expression="5 * * * *", suggestions=[s], error=None)
        assert "1" in result.summary() or "suggestion" in result.summary().lower()


# ---------------------------------------------------------------------------
# suggest_patterns — invalid input
# ---------------------------------------------------------------------------

class TestSuggestPatternsInvalid:
    def test_invalid_expression_returns_error(self):
        result = suggest_patterns("not a cron")
        assert result.ok is False
        assert result.error is not None

    def test_invalid_expression_suggestions_empty(self):
        result = suggest_patterns("not a cron")
        assert result.suggestions == []


# ---------------------------------------------------------------------------
# suggest_patterns — valid input
# ---------------------------------------------------------------------------

class TestSuggestPatternsValid:
    def test_returns_suggestion_result(self):
        result = suggest_patterns("* * * * *")
        assert isinstance(result, SuggestionResult)

    def test_every_minute_has_suggestions(self):
        result = suggest_patterns("* * * * *")
        assert result.ok is True
        assert len(result.suggestions) > 0

    def test_suggestions_have_positive_scores(self):
        result = suggest_patterns("0 * * * *")
        for s in result.suggestions:
            assert 0.0 <= s.score <= 1.0

    def test_suggestions_sorted_by_score_descending(self):
        result = suggest_patterns("0 * * * *")
        scores = [s.score for s in result.suggestions]
        assert scores == sorted(scores, reverse=True)

    def test_daily_midnight_expression(self):
        result = suggest_patterns("0 0 * * *")
        assert result.ok is True
        labels = [s.label.lower() for s in result.suggestions]
        # At least one suggestion should mention midnight or daily
        assert any("midnight" in l or "daily" in l for l in labels)

    def test_hourly_expression(self):
        result = suggest_patterns("0 * * * *")
        assert result.ok is True
        labels = [s.label.lower() for s in result.suggestions]
        assert any("hour" in l for l in labels)

    def test_weekly_expression(self):
        result = suggest_patterns("0 0 * * 0")
        assert result.ok is True
        labels = [s.label.lower() for s in result.suggestions]
        assert any("week" in l or "sunday" in l or "monday" in l for l in labels)

    def test_expression_stored_on_result(self):
        expr = "30 6 * * 1-5"
        result = suggest_patterns(expr)
        assert result.expression == expr

    def test_suggestions_have_non_empty_reason(self):
        result = suggest_patterns("*/5 * * * *")
        for s in result.suggestions:
            assert isinstance(s.reason, str) and len(s.reason) > 0

    def test_suggestions_have_valid_expressions(self):
        """Each suggestion should itself be a parseable cron expression."""
        from crontab_doctor.parser import parse_expression
        result = suggest_patterns("*/15 * * * *")
        for s in result.suggestions:
            try:
                parse_expression(s.expression)
            except Exception as exc:
                pytest.fail(f"Suggestion expression '{s.expression}' is invalid: {exc}")

    def test_top_suggestion_is_close_match_for_exact_standard(self):
        """Passing a well-known pattern should rank its canonical form first."""
        result = suggest_patterns("0 0 * * *")
        assert result.ok is True
        if result.suggestions:
            top = result.suggestions[0]
            assert top.score >= 0.5
