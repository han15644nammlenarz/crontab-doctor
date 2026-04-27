"""CLI sub-command: group cron expressions from a file."""
from __future__ import annotations

import argparse
import sys

from .cron_grouper import group_expressions
from .group_formatter import format_group_result


def build_grouper_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "group",
        help="Group cron expressions by schedule characteristics",
    )
    p.add_argument(
        "file",
        help="File containing one cron expression per line",
    )
    p.add_argument(
        "--by",
        choices=["frequency", "hour", "minute"],
        default="frequency",
        help="Grouping strategy (default: frequency)",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colour output",
    )
    return p


def cmd_group(args: argparse.Namespace) -> int:
    try:
        with open(args.file) as fh:
            lines = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 2

    result = group_expressions(lines, by=args.by)
    print(format_group_result(result, color=not args.no_color))
    return 0 if result.ok() else 1


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(prog="crontab-group")
    sub = parser.add_subparsers(dest="command")
    build_grouper_parser(sub)
    args = parser.parse_args()
    sys.exit(cmd_group(args))
