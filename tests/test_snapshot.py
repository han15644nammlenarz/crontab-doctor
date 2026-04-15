"""Tests for snapshot module and formatter."""
from __future__ import annotations

import json
import os
import pytest

from crontab_doctor.snapshot import (
    Snapshot,
    diff_snapshots,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)
from crontab_doctor.snapshot_formatter import format_diff, format_snapshot, format_snapshot_list


@pytest.fixture()
def snap_file(tmp_path):
    return str(tmp_path / "snaps.json")


def test_save_and_load_snapshot(snap_file):
    snap = save_snapshot("v1", ["* * * * *", "0 12 * * *"], path=snap_file)
    assert snap.label == "v1"
    loaded = load_snapshot("v1", path=snap_file)
    assert loaded is not None
    assert loaded.expressions == ["* * * * *", "0 12 * * *"]


def test_load_missing_snapshot_returns_none(snap_file):
    result = load_snapshot("nonexistent", path=snap_file)
    assert result is None


def test_list_snapshots_empty(snap_file):
    snaps = list_snapshots(path=snap_file)
    assert snaps == []


def test_list_snapshots_multiple(snap_file):
    save_snapshot("a", ["* * * * *"], path=snap_file)
    save_snapshot("b", ["0 0 * * *"], path=snap_file)
    snaps = list_snapshots(path=snap_file)
    assert len(snaps) == 2
    assert snaps[0].label == "a"
    assert snaps[1].label == "b"


def test_save_snapshot_persists_json(snap_file):
    save_snapshot("persist", ["5 4 * * 0"], path=snap_file)
    with open(snap_file) as fh:
        data = json.load(fh)
    assert len(data) == 1
    assert data[0]["label"] == "persist"


def test_diff_snapshots_added_removed():
    old = Snapshot(label="old", expressions=["* * * * *", "0 12 * * *"])
    new = Snapshot(label="new", expressions=["* * * * *", "30 6 * * 1"])
    diff = diff_snapshots(old, new)
    assert "0 12 * * *" in diff["removed"]
    assert "30 6 * * 1" in diff["added"]
    assert "* * * * *" in diff["unchanged"]


def test_diff_identical_snapshots():
    snap = Snapshot(label="x", expressions=["0 0 * * *"])
    diff = diff_snapshots(snap, snap)
    assert diff["added"] == []
    assert diff["removed"] == []
    assert diff["unchanged"] == ["0 0 * * *"]


def test_snapshot_repr():
    snap = Snapshot(label="test", expressions=["* * * * *"])
    r = repr(snap)
    assert "test" in r
    assert "1" in r


def test_format_snapshot_contains_label():
    snap = Snapshot(label="mylabel", expressions=["* * * * *"])
    out = format_snapshot(snap)
    assert "mylabel" in out
    assert "* * * * *" in out


def test_format_snapshot_list_empty():
    out = format_snapshot_list([])
    assert "No snapshots" in out


def test_format_snapshot_list_with_entries():
    snaps = [Snapshot(label="alpha", expressions=["0 1 * * *", "0 2 * * *"])]
    out = format_snapshot_list(snaps)
    assert "alpha" in out
    assert "2" in out


def test_format_diff_shows_added_removed():
    old = Snapshot(label="old", expressions=["* * * * *"])
    new = Snapshot(label="new", expressions=["0 0 * * *"])
    diff = diff_snapshots(old, new)
    out = format_diff(old, new, diff)
    assert "Added" in out or "+" in out
    assert "Removed" in out or "-" in out


def test_format_diff_identical():
    snap = Snapshot(label="same", expressions=["* * * * *"])
    diff = diff_snapshots(snap, snap)
    out = format_diff(snap, snap, diff)
    assert "identical" in out.lower()
