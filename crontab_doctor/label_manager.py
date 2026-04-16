"""Attach human-readable labels/descriptions to cron expressions."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_LABELS_FILE = Path.home() / ".crontab_doctor" / "labels.json"


@dataclass
class LabelEntry:
    expression: str
    label: str
    description: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "label": self.label,
            "description": self.description,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "LabelEntry":
        return cls(
            expression=d["expression"],
            label=d["label"],
            description=d.get("description", ""),
            tags=d.get("tags", []),
        )

    def __repr__(self) -> str:
        return f"LabelEntry({self.expression!r}, label={self.label!r})"


def _load(path: Path) -> Dict[str, LabelEntry]:
    if not path.exists():
        return {}
    with path.open() as fh:
        raw = json.load(fh)
    return {k: LabelEntry.from_dict(v) for k, v in raw.items()}


def _save(entries: Dict[str, LabelEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump({k: v.to_dict() for k, v in entries.items()}, fh, indent=2)


def set_label(
    expression: str,
    label: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    path: Path = DEFAULT_LABELS_FILE,
) -> LabelEntry:
    entries = _load(path)
    entry = LabelEntry(
        expression=expression,
        label=label,
        description=description,
        tags=tags or [],
    )
    entries[expression] = entry
    _save(entries, path)
    return entry


def get_label(expression: str, path: Path = DEFAULT_LABELS_FILE) -> Optional[LabelEntry]:
    return _load(path).get(expression)


def list_labels(path: Path = DEFAULT_LABELS_FILE) -> List[LabelEntry]:
    return list(_load(path).values())


def remove_label(expression: str, path: Path = DEFAULT_LABELS_FILE) -> bool:
    entries = _load(path)
    if expression not in entries:
        return False
    del entries[expression]
    _save(entries, path)
    return True
