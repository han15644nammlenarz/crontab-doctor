"""Tag manager for labelling and grouping cron expressions."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

TAGS_FILE = os.path.expanduser("~/.crontab_doctor_tags.json")


@dataclass
class TagEntry:
    expression: str
    tags: List[str] = field(default_factory=list)
    note: Optional[str] = None

    def to_dict(self) -> dict:
        return {"expression": self.expression, "tags": self.tags, "note": self.note}

    @classmethod
    def from_dict(cls, data: dict) -> "TagEntry":
        return cls(
            expression=data["expression"],
            tags=data.get("tags", []),
            note=data.get("note"),
        )


def _load(path: str = TAGS_FILE) -> Dict[str, TagEntry]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return {k: TagEntry.from_dict(v) for k, v in raw.items()}


def _save(entries: Dict[str, TagEntry], path: str = TAGS_FILE) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({k: v.to_dict() for k, v in entries.items()}, fh, indent=2)


def add_tags(expression: str, tags: List[str], note: Optional[str] = None,
             path: str = TAGS_FILE) -> TagEntry:
    """Add or update tags for a cron expression."""
    entries = _load(path)
    entry = entries.get(expression, TagEntry(expression=expression))
    for t in tags:
        if t not in entry.tags:
            entry.tags.append(t)
    if note is not None:
        entry.note = note
    entries[expression] = entry
    _save(entries, path)
    return entry


def remove_tags(expression: str, tags: List[str],
                path: str = TAGS_FILE) -> TagEntry:
    """Remove specific tags from a cron expression entry."""
    entries = _load(path)
    if expression not in entries:
        raise KeyError(f"No tag entry for expression: {expression!r}")
    entry = entries[expression]
    entry.tags = [t for t in entry.tags if t not in tags]
    entries[expression] = entry
    _save(entries, path)
    return entry


def find_by_tag(tag: str, path: str = TAGS_FILE) -> List[TagEntry]:
    """Return all entries that carry the given tag."""
    return [e for e in _load(path).values() if tag in e.tags]


def list_all(path: str = TAGS_FILE) -> List[TagEntry]:
    """Return every stored tag entry."""
    return list(_load(path).values())


def delete_entry(expression: str, path: str = TAGS_FILE) -> None:
    """Completely remove the tag entry for an expression."""
    entries = _load(path)
    entries.pop(expression, None)
    _save(entries, path)
