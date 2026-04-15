"""CLI sub-command: retry-policy — advise retry/backoff for a cron expression."""

import argparse
import sys

from .retry_policy import advise_retry


def build_retry_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Suggest retry and backoff settings for a cron expression."
    if subparsers is not None:
        parser = subparsers.add_parser("retry-policy", help=description)
    else:
        parser = argparse.ArgumentParser(
            prog="crontab-doctor retry-policy",
            description=description,
        )
    parser.add_argument(
        "expression",
        help="Cron expression in quotes, e.g. '*/5 * * * *'",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output advice as JSON",
    )
    return parser


def cmd_retry(args: argparse.Namespace) -> int:
    advice = advise_retry(args.expression)

    if args.json:
        import json
        payload = {
            "expression": advice.expression,
            "interval_minutes": advice.interval_minutes,
            "suggestions": advice.suggestions,
            "warnings": advice.warnings,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(advice.summary())

    return 1 if advice.warnings else 0


def main(argv=None) -> None:  # pragma: no cover
    parser = build_retry_parser()
    args = parser.parse_args(argv)
    sys.exit(cmd_retry(args))


if __name__ == "__main__":  # pragma: no cover
    main()
