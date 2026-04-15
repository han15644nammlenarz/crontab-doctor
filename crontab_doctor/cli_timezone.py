"""CLI sub-command: timezone — check a cron expression with a timezone."""
from __future__ import annotations

import argparse
import sys

from .timezone_checker import check_timezone


def build_timezone_parser(subparsers=None):
    description = "Check a cron expression against a given IANA timezone."
    if subparsers is not None:
        p = subparsers.add_parser("timezone", help=description)
    else:
        p = argparse.ArgumentParser(prog="crontab-doctor timezone", description=description)

    p.add_argument(
        "expression",
        help="Cron expression to check (quote it: '*/5 * * * *')",
    )
    p.add_argument(
        "--tz",
        dest="timezone",
        default=None,
        metavar="TIMEZONE",
        help="IANA timezone name, e.g. 'Europe/London'",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output result as JSON",
    )
    return p


def cmd_timezone(args) -> int:
    result = check_timezone(args.expression, timezone=getattr(args, "timezone", None))

    if getattr(args, "json", False):
        import json
        print(json.dumps({
            "expression": result.expression,
            "timezone": result.timezone,
            "timezone_valid": result.timezone_valid,
            "warnings": result.warnings,
            "errors": result.errors,
            "ok": result.ok,
        }))
    else:
        print(result.summary())

    return 0 if result.ok else 1


def main():  # pragma: no cover
    parser = build_timezone_parser()
    args = parser.parse_args()
    sys.exit(cmd_timezone(args))


if __name__ == "__main__":  # pragma: no cover
    main()
