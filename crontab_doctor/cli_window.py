"""CLI sub-command: window  — show when a cron expression fires in a time window."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .window_analyzer import analyze_window
from .window_formatter import format_window_result


def build_window_parser(subparsers: argparse.Action | None = None) -> argparse.ArgumentParser:
    kwargs = dict(
        prog="crontab-doctor window",
        description="Show when a cron expression fires within a time window.",
    )
    if subparsers is not None:
        parser = subparsers.add_parser("window", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("expression", help="Cron expression (quote it!)")
    parser.add_argument(
        "--minutes",
        type=int,
        default=60,
        metavar="N",
        help="Window size in minutes (default: 60)",
    )
    parser.add_argument(
        "--from",
        dest="from_dt",
        metavar="YYYY-MM-DDTHH:MM",
        default=None,
        help="Window start (default: now)",
    )
    parser.add_argument(
        "--no-color", action="store_true", help="Disable ANSI colour output"
    )
    return parser


def cmd_window(args: argparse.Namespace) -> int:
    from_dt = None
    if args.from_dt:
        try:
            from_dt = datetime.strptime(args.from_dt, "%Y-%m-%dT%H:%M")
        except ValueError:
            print(f"Invalid --from date: {args.from_dt}", file=sys.stderr)
            return 2

    result = analyze_window(
        args.expression,
        window_minutes=args.minutes,
        from_dt=from_dt,
    )
    print(format_window_result(result, color=not args.no_color))
    return 0 if result.ok() else 1


def main() -> None:
    parser = build_window_parser()
    args = parser.parse_args()
    sys.exit(cmd_window(args))


if __name__ == "__main__":
    main()
