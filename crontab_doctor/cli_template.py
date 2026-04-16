"""CLI commands for the template library."""
import argparse
import sys

from crontab_doctor.template_library import list_templates, find_template


def build_template_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="crontab-doctor template", description="Browse cron expression templates")
    sub = p.add_subparsers(dest="subcmd")

    ls = sub.add_parser("list", help="List available templates")
    ls.add_argument("--category", default=None, help="Filter by category")
    ls.add_argument("--tag", default=None, help="Filter by tag")
    ls.add_argument("--no-color", action="store_true")

    show = sub.add_parser("show", help="Show a specific template")
    show.add_argument("name", help="Template name")
    return p


def _c(text: str, code: str, no_color: bool) -> str:
    if no_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def cmd_template(args: argparse.Namespace) -> int:
    if args.subcmd == "list" or args.subcmd is None:
        no_color = getattr(args, "no_color", False)
        category = getattr(args, "category", None)
        tag = getattr(args, "tag", None)
        templates = list_templates(category=category, tag=tag)
        if not templates:
            print("No templates found.")
            return 0
        print(f"{_c('Name', '1', no_color):<30} {_c('Expression', '1', no_color):<20} Description")
        print("-" * 72)
        for t in templates:
            name = _c(t.name, "36", no_color)
            expr = _c(t.expression, "33", no_color)
            print(f"{name:<39} {expr:<29} {t.description}")
        return 0

    if args.subcmd == "show":
        t = find_template(args.name)
        if t is None:
            print(f"Template {args.name!r} not found.", file=sys.stderr)
            return 1
        print(f"Name       : {t.name}")
        print(f"Expression : {t.expression}")
        print(f"Description: {t.description}")
        print(f"Category   : {t.category}")
        print(f"Tags       : {', '.join(t.tags) if t.tags else '(none)'}")
        return 0

    build_template_parser().print_help()
    return 0


def main() -> None:
    p = build_template_parser()
    args = p.parse_args()
    sys.exit(cmd_template(args))


if __name__ == "__main__":
    main()
