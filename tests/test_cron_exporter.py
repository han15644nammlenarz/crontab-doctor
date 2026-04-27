"""Tests for cron_exporter and export_formatter."""
import json
import pytest

from crontab_doctor.cron_exporter import export_expression, ExportResult
from crontab_doctor.export_formatter import format_export_result


# ---------------------------------------------------------------------------
# ExportResult helpers
# ---------------------------------------------------------------------------

def test_export_result_ok_when_no_error():
    r = ExportResult(expression="* * * * *", format="json", output="{}")
    assert r.ok() is True


def test_export_result_not_ok_when_error():
    r = ExportResult(expression="bad", format="json", error="oops")
    assert r.ok() is False


def test_export_result_summary_ok():
    r = ExportResult(expression="0 * * * *", format="shell", output="x")
    assert "0 * * * *" in r.summary()
    assert "shell" in r.summary()


def test_export_result_summary_error():
    r = ExportResult(expression="bad", format="json", error="parse failed")
    assert "failed" in r.summary().lower()


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

def test_export_json_valid_expression():
    result = export_expression("0 6 * * 1", fmt="json")
    assert result.ok()
    data = json.loads(result.output)
    assert data["expression"] == "0 6 * * 1"
    assert data["fields"]["minute"] == "0"
    assert data["fields"]["hour"] == "6"


def test_export_json_includes_label_and_tags():
    result = export_expression("*/5 * * * *", fmt="json", label="my-job", tags=["prod"])
    assert result.ok()
    data = json.loads(result.output)
    assert data["label"] == "my-job"
    assert "prod" in data["tags"]


def test_export_json_invalid_expression_returns_error():
    result = export_expression("not a cron", fmt="json")
    assert not result.ok()
    assert result.output is None


# ---------------------------------------------------------------------------
# Shell export
# ---------------------------------------------------------------------------

def test_export_shell_valid_expression():
    result = export_expression("30 2 * * *", fmt="shell")
    assert result.ok()
    assert "30 2 * * *" in result.output


def test_export_shell_includes_label_as_comment():
    result = export_expression("0 0 * * *", fmt="shell", label="nightly")
    assert result.ok()
    assert "# nightly" in result.output


# ---------------------------------------------------------------------------
# Env export
# ---------------------------------------------------------------------------

def test_export_env_contains_expression():
    result = export_expression("0 12 * * *", fmt="env")
    assert result.ok()
    assert "CRON_EXPRESSION=0 12 * * *" in result.output


def test_export_env_with_label_and_tags():
    result = export_expression("0 12 * * *", fmt="env", label="noon", tags=["a", "b"])
    assert "CRON_LABEL=noon" in result.output
    assert "CRON_TAGS=a,b" in result.output


# ---------------------------------------------------------------------------
# Unknown format
# ---------------------------------------------------------------------------

def test_export_unknown_format_returns_error():
    result = export_expression("* * * * *", fmt="xml")
    assert not result.ok()
    assert "xml" in result.error.lower()


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def test_format_export_result_contains_expression():
    r = export_expression("*/10 * * * *", fmt="json")
    out = format_export_result(r)
    assert "*/10 * * * *" in out


def test_format_export_result_error_shows_error():
    r = ExportResult(expression="bad", format="json", error="parse failed")
    out = format_export_result(r)
    assert "Error" in out or "error" in out


def test_format_export_result_ok_shows_checkmark():
    r = export_expression("0 0 * * 0", fmt="shell")
    out = format_export_result(r)
    assert "✓" in out
