"""Snapshot module: save and compare crontab expression snapshots over time."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

DEFAULT_SNAPSHOT_FILE = os.path.expanduser("~/.crontab_doctor_snapshots.json")


@dataclass
class Snapshot:
    label: str
    expressions: List[str]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "expressions": self.expressions,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            label=data["label"],
            expressions=data["expressions"],
            created_at=data.get("created_at", ""),
        )

    def __repr__(self) -> str:
        return f"Snapshot(label={self.label!r}, expressions={len(self.expressions)}, created_at={self.created_at!r})"


def _load(path: str) -> List[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save(records: List[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2)


def save_snapshot(label: str, expressions: List[str], path: str = DEFAULT_SNAPSHOT_FILE) -> Snapshot:
    """Persist a named snapshot of cron expressions."""
    records = _load(path)
    snap = Snapshot(label=label, expressions=expressions)
    records.append(snap.to_dict())
    _save(records, path)
    return snap


def load_snapshot(label: str, path: str = DEFAULT_SNAPSHOT_FILE) -> Optional[Snapshot]:
    """Return the most recent snapshot with the given label, or None."""
    records = _load(path)
    matches = [r for r in records if r.get("label") == label]
    if not matches:
        return None
    return Snapshot.from_dict(matches[-1])


def list_snapshots(path: str = DEFAULT_SNAPSHOT_FILE) -> List[Snapshot]:
    """Return all stored snapshots."""
    return [Snapshot.from_dict(r) for r in _load(path)]


def diff_snapshots(old: Snapshot, new: Snapshot) -> dict:
    """Return added/removed expressions between two snapshots."""
    old_set = set(old.expressions)
    new_set = set(new.expressions)
    return {
        "added": sorted(new_set - old_set),
        "removed": sorted(old_set - new_set),
        "unchanged": sorted(old_set & new_set),
    }
