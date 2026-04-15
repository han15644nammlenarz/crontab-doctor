"""Formatter for snapshot data."""
from __future__ import annotations

from typing import List

from crontab_doctor.formatter import _colorize
from crontab_doctor.snapshot import Snapshot


def format_snapshot(snap: Snapshot) -> str:
    """Return a human-readable representation of a single snapshot."""
    lines = [
        _colorize(f"Snapshot: {snap.label}", "cyan"),
        f"  Created : {snap.created_at}",
        f"  Entries : {len(snap.expressions)}",
    ]
    for expr in snap.expressions:
        lines.append(f"    - {expr}")
    return "\n".join(lines)


def format_snapshot_list(snapshots: List[Snapshot]) -> str:
    """Return a summary list of all snapshots."""
    if not snapshots:
        return _colorize("No snapshots stored.", "yellow")
    lines = [_colorize(f"{'Label':<30} {'Entries':>7}  Created", "cyan")]
    lines.append("-" * 60)
    for snap in snapshots:
        lines.append(f"{snap.label:<30} {len(snap.expressions):>7}  {snap.created_at}")
    return "\n".join(lines)


def format_diff(old: Snapshot, new: Snapshot, diff: dict) -> str:
    """Return a coloured diff between two snapshots."""
    lines = [
        _colorize(f"Diff: {old.label!r} → {new.label!r}", "cyan"),
        "",
    ]
    if diff["added"]:
        lines.append(_colorize("  Added:", "green"))
        for expr in diff["added"]:
            lines.append(_colorize(f"    + {expr}", "green"))
    if diff["removed"]:
        lines.append(_colorize("  Removed:", "red"))
        for expr in diff["removed"]:
            lines.append(_colorize(f"    - {expr}", "red"))
    if diff["unchanged"]:
        lines.append("  Unchanged:")
        for expr in diff["unchanged"]:
            lines.append(f"    = {expr}")
    if not diff["added"] and not diff["removed"]:
        lines.append(_colorize("  Snapshots are identical.", "green"))
    return "\n".join(lines)
