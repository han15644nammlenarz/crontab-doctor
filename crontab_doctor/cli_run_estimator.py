"""CLI sub-command: estimate how many times a cron job runs in a time window."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .run_estimator import estimate_runs
from .formatter import _colorize


def build_estimator_parser(subparsers=None) -> argparse.ArgumentParser:
    desc = "Estimate how many times a cron expression fires in a time window."
    if subparsers is not None:
        p = subparsers.add_parser("estimate", help=desc, description=desc)
    else:
        p = argparse.ArgumentParser(prog="crontab-doctor estimate", description=desc)

    p.add_argument("expression", help="Cron expression (quote it!), e.g. '*/5 * * * *'")
    p.add_argument(
        "--hours",
        type=int,
        default=24,
        metavar="N",
        help="Window size in hours (default: 24)",
    )
    p.add_argument(
        "--from",
        dest="from_dt",
        default=None,
        metavar="YYYY-MM-DDTHH:MM",
        help="Start of window (default: now)",
    )
    p.add_argument("--no-color", action="store_true", help="Disable colored output")
    return p


def cmd_estimate(args: argparse.Namespace) -> int:
    from_dt = None
    if args.from_dt:
        try:
            from_dt = datetime.fromisoformat(args.from_dt)
        except ValueError:
            print(f"Error: invalid --from value '{args.from_dt}'. Use YYYY-MM-DDTHH:MM.",
                  file=sys.stderr)
            return 2

    result = estimate_runs(args.expression, window_hours=args.hours, from_dt=from_dt)
    use_color = not args.no_color

    if not result.ok():
        msg = _colorize(f"✗ {result.error}", "red") if use_color else f"✗ {result.error}"
        print(msg)
        return 1

    header = _colorize(f"Expression : {result.expression}", "cyan") if use_color else f"Expression : {result.expression}"
    print(header)
    print(f"Window     : {result.window_hours} hour(s)")
    print(f"Run count  : {result.count}")
    if result.first_run:
        print(f"First run  : {result.first_run.strftime('%Y-%m-%d %H:%M')}")
    if result.last_run and result.last_run != result.first_run:
        print(f"Last run   : {result.last_run.strftime('%Y-%m-%d %H:%M')}")
    for w in result.warnings:
        warn = _colorize(f"⚠ {w}", "yellow") if use_color else f"⚠ {w}"
        print(warn)

    return 0


def main() -> None:  # pragma: no cover
    parser = build_estimator_parser()
    args = parser.parse_args()
    sys.exit(cmd_estimate(args))


if __name__ == "__main__":  # pragma: no cover
    main()
