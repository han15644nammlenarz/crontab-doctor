"""Pause/resume tracker for cron expressions with optional reason and expiry."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

_DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".crontab_doctor", "paused.json")


@dataclass
class PauseEntry:
    expression: str
    reason: str
    paused_at: str
    resume_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "reason": self.reason,
            "paused_at": self.paused_at,
            "resume_at": self.resume_at,
        }

    @staticmethod
    def from_dict(d: dict) -> "PauseEntry":
        return PauseEntry(
            expression=d["expression"],
            reason=d.get("reason", ""),
            paused_at=d["paused_at"],
            resume_at=d.get("resume_at"),
        )

    def __repr__(self) -> str:
        return f"PauseEntry(expression={self.expression!r}, reason={self.reason!r})"

    def is_expired(self) -> bool:
        """Return True if resume_at is set and is in the past."""
        if not self.resume_at:
            return False
        try:
            resume_dt = datetime.fromisoformat(self.resume_at)
            if resume_dt.tzinfo is None:
                resume_dt = resume_dt.replace(tzinfo=timezone.utc)
            return datetime.now(timezone.utc) >= resume_dt
        except ValueError:
            return False


def _load(path: str) -> Dict[str, dict]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save(data: Dict[str, dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def pause_expression(
    expression: str,
    reason: str = "",
    resume_at: Optional[str] = None,
    path: str = _DEFAULT_PATH,
) -> PauseEntry:
    data = _load(path)
    now = datetime.now(timezone.utc).isoformat()
    entry = PauseEntry(expression=expression, reason=reason, paused_at=now, resume_at=resume_at)
    data[expression] = entry.to_dict()
    _save(data, path)
    return entry


def resume_expression(expression: str, path: str = _DEFAULT_PATH) -> bool:
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def list_paused(path: str = _DEFAULT_PATH) -> List[PauseEntry]:
    data = _load(path)
    return [PauseEntry.from_dict(v) for v in data.values()]


def is_paused(expression: str, path: str = _DEFAULT_PATH) -> bool:
    data = _load(path)
    if expression not in data:
        return False
    entry = PauseEntry.from_dict(data[expression])
    if entry.is_expired():
        resume_expression(expression, path=path)
        return False
    return True
