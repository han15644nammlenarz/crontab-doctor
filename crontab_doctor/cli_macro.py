"""CLI commands for macro expansion."""

import argparse
import sys

from crontab_doctor.macro_expander import expand_macro, list_macros, BUILTIN_MACROS, _DESCRIPTIONS


def build_macro_parser(subparsers=None):
    desc = "Expand cron macro shortcuts into standard expressions"
    if subparsers is not None:
        p = subparsers.add_parser("macro", help=desc)
    else:
        p = argparse.ArgumentParser(prog="crontab-doctor macro", description=desc)
    sub = p.add_subparsers(dest="macro_cmd")

    expand_p = sub.add_parser("expand", help="Expand a named macro")
    expand_p.add_argument("name", help="Macro name to expand")

    sub.add_parser("list", help="List all available macros")
    return p


def cmd_macro(args) -> int:
    if args.macro_cmd == "expand":
        result = expand_macro(args.name)
        print(result.summary())
        return 0 if result.ok else 1

    if args.macro_cmd == "list":
        print(f"{'Macro':<25} {'Expression':<20} Description")
        print("-" * 70)
        for name in list_macros():
            expr = BUILTIN_MACROS[name]
            desc = _DESCRIPTIONS.get(name, "")
            print(f"{name:<25} {expr:<20} {desc}")
        return 0

    print("No macro subcommand given. Use 'expand' or 'list'.", file=sys.stderr)
    return 1


def main():
    parser = build_macro_parser()
    args = parser.parse_args()
    sys.exit(cmd_macro(args))


if __name__ == "__main__":
    main()
