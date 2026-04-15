"""CLI sub-commands for the tag manager (tags add / remove / list / find)."""
from __future__ import annotations

import argparse
import sys

from crontab_doctor.tag_formatter import format_tag_entry, format_tag_list, format_tag_summary
from crontab_doctor.tag_manager import (
    TAGS_FILE,
    add_tags,
    delete_entry,
    find_by_tag,
    list_all,
    remove_tags,
)


def build_tag_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register 'tags' sub-command with its own sub-commands."""
    tag_parser = subparsers.add_parser("tags", help="Manage tags for cron expressions")
    tag_sub = tag_parser.add_subparsers(dest="tag_cmd", required=True)

    # tags add
    p_add = tag_sub.add_parser("add", help="Add tags to an expression")
    p_add.add_argument("expression", help="Cron expression to tag")
    p_add.add_argument("tags", nargs="+", help="Tags to add")
    p_add.add_argument("--note", default=None, help="Optional note")
    p_add.add_argument("--file", default=TAGS_FILE, dest="tags_file")

    # tags remove
    p_rm = tag_sub.add_parser("remove", help="Remove tags from an expression")
    p_rm.add_argument("expression")
    p_rm.add_argument("tags", nargs="+")
    p_rm.add_argument("--file", default=TAGS_FILE, dest="tags_file")

    # tags list
    p_ls = tag_sub.add_parser("list", help="List all tagged expressions")
    p_ls.add_argument("--file", default=TAGS_FILE, dest="tags_file")
    p_ls.add_argument("--no-color", action="store_true")

    # tags find
    p_find = tag_sub.add_parser("find", help="Find expressions by tag")
    p_find.add_argument("tag", help="Tag to search for")
    p_find.add_argument("--file", default=TAGS_FILE, dest="tags_file")
    p_find.add_argument("--no-color", action="store_true")

    # tags delete
    p_del = tag_sub.add_parser("delete", help="Delete all tags for an expression")
    p_del.add_argument("expression")
    p_del.add_argument("--file", default=TAGS_FILE, dest="tags_file")


def cmd_tags(args: argparse.Namespace) -> int:
    """Dispatch tag sub-commands; return exit code."""
    color = not getattr(args, "no_color", False)
    try:
        if args.tag_cmd == "add":
            entry = add_tags(args.expression, args.tags,
                             note=args.note, path=args.tags_file)
            print(format_tag_entry(entry, color=color))

        elif args.tag_cmd == "remove":
            entry = remove_tags(args.expression, args.tags, path=args.tags_file)
            print(format_tag_entry(entry, color=color))

        elif args.tag_cmd == "list":
            entries = list_all(path=args.tags_file)
            print(format_tag_list(entries, color=color))
            print(format_tag_summary(entries, color=color))

        elif args.tag_cmd == "find":
            entries = find_by_tag(args.tag, path=args.tags_file)
            print(format_tag_list(entries, color=color))

        elif args.tag_cmd == "delete":
            delete_entry(args.expression, path=args.tags_file)
            print(f"Deleted tags for: {args.expression}")

    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0
