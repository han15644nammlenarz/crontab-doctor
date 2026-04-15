"""history.py — Track and persist a history of audited crontab expressions.

Provides a simple JSON-backed store so users can review past audits,
spot regressions, and compare how a crontab has changed over time.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

# Default location: ~/.config/crontab-doctor/history.json
_DEFAULT_HISTORY_DIR = Path.home() / ".config" / "crontab-doctor"
_DEFAULT_HISTORY_FILE = _DEFAULT_HISTORY_DIR / "history.json"

# Maximum number of entries kept in the history file before the oldest
# entries are pruned automatically.
_MAX_ENTRIES = 500


@dataclass
class HistoryEntry:
    """A single audit record persisted to history."""

    expression: str
    command: Optional[str]
    timestamp: str  # ISO-8601 UTC
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    explanation: Optional[str] = None

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        return cls(
            expression=data["expression"],
            command=data.get("command"),
            timestamp=data["timestamp"],
            valid=data["valid"],
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            explanation=data.get("explanation"),
        )

    def __repr__(self) -> str:  # pragma: no cover
        status = "valid" if self.valid else "invalid"
        return f"<HistoryEntry {self.expression!r} {status} at {self.timestamp}>"


def _load(path: Path) -> List[dict]:
    """Load raw history entries from *path*; return an empty list if missing."""
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def _save(entries: List[dict], path: Path) -> None:
    """Persist *entries* to *path*, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(entries, fh, indent=2)


def record(
    expression: str,
    valid: bool,
    *,
    command: Optional[str] = None,
    errors: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
    explanation: Optional[str] = None,
    history_file: Optional[Path] = None,
) -> HistoryEntry:
    """Append an audit result to the history store and return the entry.

    Parameters
    ----------
    expression:
        The raw crontab expression that was audited.
    valid:
        Whether the expression passed validation.
    command:
        Optional command string associated with the crontab line.
    errors:
        List of validation error messages.
    warnings:
        List of validation warning messages.
    explanation:
        Human-readable explanation of the schedule.
    history_file:
        Override the default history file path (useful for testing).
    """
    path = history_file or _DEFAULT_HISTORY_FILE
    entry = HistoryEntry(
        expression=expression,
        command=command,
        timestamp=datetime.now(timezone.utc).isoformat(),
        valid=valid,
        errors=errors or [],
        warnings=warnings or [],
        explanation=explanation,
    )
    raw = _load(path)
    raw.append(entry.to_dict())
    # Prune oldest entries if we exceed the cap
    if len(raw) > _MAX_ENTRIES:
        raw = raw[-_MAX_ENTRIES:]
    _save(raw, path)
    return entry


def load_history(
    *,
    history_file: Optional[Path] = None,
    limit: int = 50,
    expression_filter: Optional[str] = None,
) -> List[HistoryEntry]:
    """Return recent history entries, newest first.

    Parameters
    ----------
    history_file:
        Override the default history file path.
    limit:
        Maximum number of entries to return.
    expression_filter:
        If provided, only entries whose expression contains this substring
        are returned.
    """
    path = history_file or _DEFAULT_HISTORY_FILE
    raw = _load(path)
    entries = [HistoryEntry.from_dict(d) for d in raw]
    if expression_filter:
        entries = [e for e in entries if expression_filter in e.expression]
    # Newest first
    entries.reverse()
    return entries[:limit]


def clear_history(*, history_file: Optional[Path] = None) -> int:
    """Delete all history entries and return the number removed."""
    path = history_file or _DEFAULT_HISTORY_FILE
    raw = _load(path)
    count = len(raw)
    _save([], path)
    return count
