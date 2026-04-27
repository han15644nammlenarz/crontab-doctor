"""CLI sub-command: sort — rank cron expressions by various criteria."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .cron_sorter import sort_expressions, VALID_KEYS
from .sort_formatter import format_sort_result


def build_sorter_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser("sort", help="Sort cron expressions by frequency, next run, expression, or label")
    p.add_argument("expressions", nargs="+", metavar="EXPR", help="Cron expressions to sort")
    p.add_argument(
        "--by",
        dest="sort_by",
        default="frequency",
        choices=list(VALID_KEYS),
        help="Sort key (default: frequency)",
    )
    p.add_argument(
        "--labels",
        nargs="+",
        metavar="LABEL",
        default=None,
        help="Optional labels aligned with expressions",
    )
    p.add_argument("--reverse", action="store_true", help="Reverse sort order")
    p.add_argument("--no-color", action="store_true", help="Disable color output")
    return p


def cmd_sort(args: argparse.Namespace) -> int:
    labels: Optional[List[Optional[str]]] = args.labels
    result = sort_expressions(
        expressions=args.expressions,
        sort_by=args.sort_by,
        labels=labels,
        reverse=args.reverse,
    )
    print(format_sort_result(result, use_color=not args.no_color))
    return 0 if result.ok() else 1


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(prog="crontab-sort", description="Sort cron expressions")
    sub = parser.add_subparsers(dest="command")
    build_sorter_parser(sub)
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    sys.exit(cmd_sort(args))
