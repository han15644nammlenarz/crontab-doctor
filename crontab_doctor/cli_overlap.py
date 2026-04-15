"""CLI sub-command: overlap — detect scheduling overlaps across expressions."""

import argparse
import sys

from .overlap_reporter import build_overlap_report
from .overlap_formatter import format_overlap_report


def build_overlap_parser(subparsers=None):
    description = "Detect scheduling overlaps between multiple cron expressions."
    if subparsers is not None:
        p = subparsers.add_parser("overlap", help=description)
    else:
        p = argparse.ArgumentParser(prog="crontab-doctor overlap", description=description)
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Two or more cron expressions to compare (quote each one).",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable coloured output.",
    )
    return p


def cmd_overlap(args) -> int:
    if len(args.expressions) < 2:
        print("[ERROR] Provide at least two expressions to compare.", file=sys.stderr)
        return 1

    report = build_overlap_report(args.expressions)
    print(format_overlap_report(report, color=not args.no_color))
    return 1 if report.has_conflicts() or report.error else 0


def main():
    parser = build_overlap_parser()
    args = parser.parse_args()
    sys.exit(cmd_overlap(args))


if __name__ == "__main__":
    main()
