"""CLI sub-commands for the linter feature."""

import argparse
import sys
from typing import List

from .lint import lint_expression
from .lint_formatter import format_lint_results, format_lint_summary


def build_lint_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "lint",
        help="Lint one or more crontab expressions for suspicious patterns.",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Crontab expression(s) to lint, e.g. '0 0 * * *'.",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output.",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a summary table after individual results.",
    )
    p.set_defaults(func=cmd_lint)


def cmd_lint(args: argparse.Namespace) -> int:
    color = not args.no_color
    results: dict = {}
    exit_code = 0

    for raw in args.expressions:
        warnings = lint_expression(raw)
        results[raw] = warnings
        print(format_lint_results(raw, warnings, color=color))
        print()
        if any(w.severity == "warning" for w in warnings):
            exit_code = 1

    if args.summary:
        print(format_lint_summary(results, color=color))

    return exit_code


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="crontab-lint",
        description="Lint crontab expressions for suspicious patterns.",
    )
    subparsers = parser.add_subparsers(dest="command")
    build_lint_parser(subparsers)
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    sys.exit(args.func(args))
