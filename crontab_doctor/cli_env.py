"""CLI sub-command: env — check environment variables used in cron commands."""
from __future__ import annotations

import argparse
import sys
from typing import List

from crontab_doctor.env_checker import check_env
from crontab_doctor.env_formatter import format_env_result, format_env_results


def build_env_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Check environment variables referenced in cron commands."
    if subparsers is not None:
        parser = subparsers.add_parser("env", help=description)
    else:
        parser = argparse.ArgumentParser(
            prog="crontab-doctor env", description=description
        )
    parser.add_argument(
        "expression",
        help="Cron expression (quote it), e.g. '*/5 * * * *'",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default=None,
        help="Shell command associated with the cron job.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output.",
    )
    return parser


def cmd_env(args: argparse.Namespace) -> int:
    color = not args.no_color
    result = check_env(expression=args.expression, command=args.command)
    print(format_env_result(result, color=color))
    return 0 if result.ok else 1


def main(argv: List[str] | None = None) -> None:
    parser = build_env_parser()
    args = parser.parse_args(argv)
    sys.exit(cmd_env(args))


if __name__ == "__main__":
    main()
