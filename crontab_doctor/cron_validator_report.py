"""Aggregate validation report for multiple cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse_expression, ParseError
from .validator import validate, ValidationError
from .lint import lint


@dataclass
class ExpressionReport:
    expression: str
    command: Optional[str]
    parse_error: Optional[str]
    validation_errors: List[str]
    lint_warnings: List[str]

    @property
    def ok(self) -> bool:
        return self.parse_error is None and len(self.validation_errors) == 0

    def summary(self) -> str:
        if self.parse_error:
            return f"[INVALID] {self.expression!r}: {self.parse_error}"
        if self.validation_errors:
            joined = "; ".join(self.validation_errors)
            return f"[INVALID] {self.expression!r}: {joined}"
        warnings = len(self.lint_warnings)
        if warnings:
            return f"[OK] {self.expression!r} ({warnings} lint warning(s))"
        return f"[OK] {self.expression!r}"


@dataclass
class ValidationReport:
    reports: List[ExpressionReport] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None and all(r.ok for r in self.reports)

    @property
    def total(self) -> int:
        return len(self.reports)

    @property
    def valid_count(self) -> int:
        return sum(1 for r in self.reports if r.ok)

    @property
    def invalid_count(self) -> int:
        return self.total - self.valid_count

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        return (
            f"{self.total} expression(s) checked: "
            f"{self.valid_count} valid, {self.invalid_count} invalid."
        )


def build_validation_report(expressions: List[str]) -> ValidationReport:
    """Validate and lint a list of raw cron expression strings."""
    if not expressions:
        return ValidationReport(error="No expressions provided.")

    reports: List[ExpressionReport] = []
    for raw in expressions:
        raw = raw.strip()
        parse_err: Optional[str] = None
        val_errors: List[str] = []
        lint_warnings: List[str] = []
        command: Optional[str] = None

        try:
            parsed = parse_expression(raw)
            command = parsed.command
            try:
                validate(parsed)
            except ValidationError as ve:
                val_errors = [str(ve)]
            lint_results = lint(parsed)
            lint_warnings = [w.message for w in lint_results]
        except ParseError as pe:
            parse_err = str(pe)

        reports.append(ExpressionReport(
            expression=raw,
            command=command,
            parse_error=parse_err,
            validation_errors=val_errors,
            lint_warnings=lint_warnings,
        ))

    return ValidationReport(reports=reports)
