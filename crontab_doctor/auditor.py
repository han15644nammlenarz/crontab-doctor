"""High-level auditor that ties together parsing, validation, explanation, and conflict detection."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse_expression, ParseError, CronExpression
from .validator import CronValidator, ValidationError
from .explainer import explain
from .conflict_detector import Conflict, detect_conflicts


@dataclass
class AuditResult:
    raw: str
    expression: Optional[CronExpression] = None
    parse_error: Optional[str] = None
    validation_errors: List[ValidationError] = field(default_factory=list)
    explanation: Optional[str] = None
    is_valid: bool = False

    def summary(self) -> str:
        lines = [f"Expression : {self.raw}"]
        if self.parse_error:
            lines.append(f"Parse error: {self.parse_error}")
        elif self.validation_errors:
            lines.append("Validation errors:")
            for e in self.validation_errors:
                lines.append(f"  - {e}")
        else:
            lines.append(f"Valid      : yes")
            lines.append(f"Explanation: {self.explanation}")
        return "\n".join(lines)


def audit_expression(raw: str) -> AuditResult:
    """Parse, validate, and explain a single cron expression."""
    result = AuditResult(raw=raw)
    try:
        expr = parse_expression(raw)
    except ParseError as exc:
        result.parse_error = str(exc)
        return result

    result.expression = expr
    validator = CronValidator(expr)
    errors = validator.validate()
    if errors:
        result.validation_errors = errors
        return result

    result.is_valid = True
    result.explanation = explain(expr)
    return result


def audit_many(raws: List[str]) -> tuple:
    """Audit multiple expressions and detect conflicts among valid ones.

    Returns (List[AuditResult], List[Conflict]).
    """
    results = [audit_expression(r) for r in raws]
    valid_pairs = [
        (r.raw, r.expression)
        for r in results
        if r.is_valid and r.expression is not None
    ]
    conflicts = detect_conflicts(valid_pairs)
    return results, conflicts
