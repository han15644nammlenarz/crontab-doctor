"""CLI sub-commands for snapshot management."""
from __future__ import annotations

import argparse
import sys

from crontab_doctor.snapshot import (
    diff_snapshots,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)
from crontab_doctor.snapshot_formatter import format_diff, format_snapshot, format_snapshot_list


def build_snapshot_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    sp = subparsers.add_parser("snapshot", help="Manage cron expression snapshots")
    sub = sp.add_subparsers(dest="snapshot_cmd", required=True)

    # save
    p_save = sub.add_parser("save", help="Save a snapshot")
    p_save.add_argument("label", help="Snapshot label")
    p_save.add_argument("expressions", nargs="+", help="Cron expressions to snapshot")

    # show
    p_show = sub.add_parser("show", help="Show a saved snapshot")
    p_show.add_argument("label", help="Snapshot label")

    # list
    sub.add_parser("list", help="List all snapshots")

    # diff
    p_diff = sub.add_parser("diff", help="Diff two snapshots")
    p_diff.add_argument("old_label", help="Older snapshot label")
    p_diff.add_argument("new_label", help="Newer snapshot label")


def cmd_snapshot(args: argparse.Namespace) -> int:
    cmd = args.snapshot_cmd

    if cmd == "save":
        snap = save_snapshot(args.label, args.expressions)
        print(format_snapshot(snap))
        return 0

    if cmd == "show":
        snap = load_snapshot(args.label)
        if snap is None:
            print(f"No snapshot found with label '{args.label}'.", file=sys.stderr)
            return 1
        print(format_snapshot(snap))
        return 0

    if cmd == "list":
        snaps = list_snapshots()
        print(format_snapshot_list(snaps))
        return 0

    if cmd == "diff":
        old = load_snapshot(args.old_label)
        new = load_snapshot(args.new_label)
        missing = [lbl for lbl, s in ((args.old_label, old), (args.new_label, new)) if s is None]
        if missing:
            for lbl in missing:
                print(f"Snapshot not found: '{lbl}'", file=sys.stderr)
            return 1
        result = diff_snapshots(old, new)  # type: ignore[arg-type]
        print(format_diff(old, new, result))  # type: ignore[arg-type]
        return 0

    return 1
