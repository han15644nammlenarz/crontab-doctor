"""CLI sub-command: benchmark — rank cron expressions by frequency."""
from __future__ import annotations

import argparse
import sys

from .cron_benchmark import benchmark_expressions
from .benchmark_formatter import format_benchmark


def build_benchmark_parser(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "benchmark",
        help="Rank cron expressions by run frequency.",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="One or more cron expressions to benchmark.",
    )
    p.add_argument(
        "--labels",
        nargs="*",
        metavar="LABEL",
        default=None,
        help="Optional labels matching the order of expressions.",
    )
    return p


def cmd_benchmark(args: argparse.Namespace) -> int:
    result = benchmark_expressions(args.expressions, labels=args.labels)
    print(format_benchmark(result))
    return 0 if result.ok else 1


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(prog="crontab-benchmark")
    sub = parser.add_subparsers(dest="command")
    build_benchmark_parser(sub)
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    sys.exit(cmd_benchmark(args))
