"""Export cron expressions to various formats (JSON, TOML-like, shell)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse_expression, ParseError


@dataclass
class ExportResult:
    expression: str
    format: str
    output: Optional[str] = None
    error: Optional[str] = None
    label: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def ok(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"Export failed: {self.error}"
        return f"Exported '{self.expression}' as {self.format}"


def _to_json(expr_str: str, label: Optional[str], tags: List[str]) -> str:
    parsed = parse_expression(expr_str)
    data = {
        "expression": expr_str,
        "fields": {
            "minute": parsed.minute,
            "hour": parsed.hour,
            "day_of_month": parsed.day_of_month,
            "month": parsed.month,
            "day_of_week": parsed.day_of_week,
        },
        "command": parsed.command,
        "label": label,
        "tags": tags,
    }
    return json.dumps(data, indent=2)


def _to_shell(expr_str: str, label: Optional[str]) -> str:
    parsed = parse_expression(expr_str)
    comment = f"# {label}\n" if label else ""
    command = parsed.command or "# <command>"
    return f"{comment}{expr_str}\t{command}"


def _to_env(expr_str: str, label: Optional[str], tags: List[str]) -> str:
    lines = []
    if label:
        lines.append(f"CRON_LABEL={label}")
    lines.append(f"CRON_EXPRESSION={expr_str}")
    if tags:
        lines.append(f"CRON_TAGS={','.join(tags)}")
    return "\n".join(lines)


def export_expression(
    expr_str: str,
    fmt: str = "json",
    label: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> ExportResult:
    tags = tags or []
    fmt = fmt.lower()
    try:
        if fmt == "json":
            output = _to_json(expr_str, label, tags)
        elif fmt == "shell":
            output = _to_shell(expr_str, label)
        elif fmt == "env":
            output = _to_env(expr_str, label, tags)
        else:
            return ExportResult(
                expression=expr_str,
                format=fmt,
                error=f"Unknown format '{fmt}'. Choose from: json, shell, env",
            )
    except ParseError as exc:
        return ExportResult(expression=expr_str, format=fmt, error=str(exc))
    return ExportResult(
        expression=expr_str,
        format=fmt,
        output=output,
        label=label,
        tags=tags,
    )
