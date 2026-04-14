"""Tests for conflict_detector and auditor modules."""

import pytest
from crontab_doctor.conflict_detector import _expand_field, _expressions_overlap, detect_conflicts, Conflict
from crontab_doctor.parser import parse_expression
from crontab_doctor.auditor import audit_expression, audit_many


# --- _expand_field ---

def test_expand_star():
    assert _expand_field("*", 0, 4) == {0, 1, 2, 3, 4}


def test_expand_single_value():
    assert _expand_field("5", 0, 59) == {5}


def test_expand_range():
    assert _expand_field("1-3", 0, 59) == {1, 2, 3}


def test_expand_step():
    assert _expand_field("*/15", 0, 59) == {0, 15, 30, 45}


def test_expand_list():
    assert _expand_field("1,3,5", 0, 59) == {1, 3, 5}


# --- _expressions_overlap ---

def test_overlap_identical_expressions():
    a = parse_expression("0 12 * * *")
    b = parse_expression("0 12 * * *")
    assert _expressions_overlap(a, b) is True


def test_no_overlap_different_hours():
    a = parse_expression("0 8 * * *")
    b = parse_expression("0 9 * * *")
    assert _expressions_overlap(a, b) is False


def test_overlap_wildcard_vs_specific():
    a = parse_expression("0 * * * *")
    b = parse_expression("0 6 * * *")
    assert _expressions_overlap(a, b) is True


# --- detect_conflicts ---

def test_detect_conflicts_finds_overlap():
    exprs = [
        ("0 12 * * *", parse_expression("0 12 * * *")),
        ("0 12 * * *", parse_expression("0 12 * * *")),
    ]
    conflicts = detect_conflicts(exprs)
    assert len(conflicts) == 1
    assert isinstance(conflicts[0], Conflict)


def test_detect_conflicts_no_overlap():
    exprs = [
        ("0 8 * * *", parse_expression("0 8 * * *")),
        ("0 9 * * *", parse_expression("0 9 * * *")),
    ]
    assert detect_conflicts(exprs) == []


# --- audit_expression ---

def test_audit_valid_expression():
    result = audit_expression("30 6 * * 1")
    assert result.is_valid
    assert result.explanation is not None
    assert result.parse_error is None
    assert result.validation_errors == []


def test_audit_invalid_minute():
    result = audit_expression("99 6 * * *")
    assert not result.is_valid
    assert result.validation_errors


def test_audit_parse_error():
    result = audit_expression("not a cron")
    assert not result.is_valid
    assert result.parse_error is not None


def test_audit_summary_valid():
    result = audit_expression("0 0 * * *")
    summary = result.summary()
    assert "Valid" in summary
    assert "Explanation" in summary


# --- audit_many ---

def test_audit_many_returns_conflicts():
    results, conflicts = audit_many(["0 12 * * *", "0 12 * * *", "0 8 * * *"])
    assert len(results) == 3
    assert len(conflicts) == 1


def test_audit_many_no_conflicts():
    _, conflicts = audit_many(["0 6 * * *", "0 18 * * *"])
    assert conflicts == []
