"""CLI sub-command: estimate compute cost of a cron expression."""
from __future__ import annotations
import argparse
import sys
from crontab_doctor.cost_estimator import estimate_cost


def build_cost_parser(subparsers=None):
    desc = "Estimate resource cost of a cron expression."
    if subparsers is not None:
        p = subparsers.add_parser("cost", help=desc)
    else:
        p = argparse.ArgumentParser(prog="crontab-doctor cost", description=desc)
    p.add_argument("expression", help="Cron expression (quote it)")
    p.add_argument(
        "--cost-per-run",
        type=float,
        default=1.0,
        metavar="UNITS",
        help="Cost units consumed per execution (default: 1.0)",
    )
    p.add_argument(
        "--window",
        type=int,
        default=24,
        metavar="HOURS",
        help="Sampling window in hours (default: 24)",
    )
    return p


def cmd_cost(args) -> int:
    est = estimate_cost(
        args.expression,
        cost_per_run=args.cost_per_run,
        window_hours=args.window,
    )
    print(est.summary())
    return 0 if est.ok() else 1


def main():
    p = build_cost_parser()
    args = p.parse_args()
    sys.exit(cmd_cost(args))


if __name__ == "__main__":
    main()
