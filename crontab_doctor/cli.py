"""Command-line interface for crontab-doctor."""

import sys
import argparse
from typing import List, Optional

from crontab_doctor.auditor import audit_expression, audit_many
from crontab_doctor.formatter import format_audit_result, format_conflicts, format_summary
from crontab_doctor.conflict_detector import detect_conflicts
from crontab_doctor.parser import ParseError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-doctor",
        description="Audit and validate crontab expressions with human-readable explanations.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_cmd = subparsers.add_parser("check", help="Validate a single crontab expression")
    check_cmd.add_argument("expression", help="Crontab expression (quoted), e.g. '*/5 * * * * /cmd'")
    check_cmd.add_argument("--no-color", action="store_true", help="Disable colored output")

    audit_cmd = subparsers.add_parser("audit", help="Audit a crontab file for errors and conflicts")
    audit_cmd.add_argument("file", help="Path to crontab file")
    audit_cmd.add_argument("--no-color", action="store_true", help="Disable colored output")
    audit_cmd.add_argument("--no-conflicts", action="store_true", help="Skip conflict detection")

    return parser


def cmd_check(expression: str, color: bool) -> int:
    result = audit_expression(expression)
    print(format_audit_result(result, color=color))
    return 0 if result.is_valid else 1


def cmd_audit(filepath: str, color: bool, detect: bool) -> int:
    try:
        with open(filepath) as fh:
            lines = [ln.rstrip() for ln in fh if ln.strip() and not ln.strip().startswith("#")]
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 2

    results = audit_many(lines)
    exit_code = 0
    for result in results:
        print(format_audit_result(result, color=color))
        if not result.is_valid:
            exit_code = 1

    if detect:
        valid_exprs = [r.expression for r in results if r.expression is not None]
        conflicts = detect_conflicts(valid_exprs)
        if conflicts:
            print(format_conflicts(conflicts, color=color))
            exit_code = max(exit_code, 1)

    print(format_summary(results, color=color))
    return exit_code


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    color = not getattr(args, "no_color", False)

    if args.command == "check":
        return cmd_check(args.expression, color=color)
    elif args.command == "audit":
        return cmd_audit(args.file, color=color, detect=not args.no_conflicts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
