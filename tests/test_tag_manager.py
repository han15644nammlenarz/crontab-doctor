"""Tests for crontab_doctor.tag_manager."""
import pytest

from crontab_doctor.tag_manager import (
    TagEntry,
    add_tags,
    delete_entry,
    find_by_tag,
    list_all,
    remove_tags,
)

EXPR = "0 9 * * 1-5"
EXPR2 = "*/15 * * * *"


@pytest.fixture()
def tags_file(tmp_path):
    return str(tmp_path / "tags.json")


def test_add_tags_creates_entry(tags_file):
    entry = add_tags(EXPR, ["work", "daily"], path=tags_file)
    assert isinstance(entry, TagEntry)
    assert "work" in entry.tags
    assert "daily" in entry.tags


def test_add_tags_with_note(tags_file):
    entry = add_tags(EXPR, ["backup"], note="nightly backup", path=tags_file)
    assert entry.note == "nightly backup"


def test_add_tags_idempotent(tags_file):
    add_tags(EXPR, ["work"], path=tags_file)
    entry = add_tags(EXPR, ["work"], path=tags_file)
    assert entry.tags.count("work") == 1


def test_add_tags_accumulates(tags_file):
    add_tags(EXPR, ["work"], path=tags_file)
    entry = add_tags(EXPR, ["daily"], path=tags_file)
    assert "work" in entry.tags
    assert "daily" in entry.tags


def test_remove_tags(tags_file):
    add_tags(EXPR, ["work", "daily"], path=tags_file)
    entry = remove_tags(EXPR, ["daily"], path=tags_file)
    assert "daily" not in entry.tags
    assert "work" in entry.tags


def test_remove_tags_missing_expression_raises(tags_file):
    with pytest.raises(KeyError):
        remove_tags("1 2 3 4 5", ["x"], path=tags_file)


def test_find_by_tag_returns_matching(tags_file):
    add_tags(EXPR, ["work"], path=tags_file)
    add_tags(EXPR2, ["monitoring"], path=tags_file)
    results = find_by_tag("work", path=tags_file)
    assert len(results) == 1
    assert results[0].expression == EXPR


def test_find_by_tag_no_match(tags_file):
    add_tags(EXPR, ["work"], path=tags_file)
    assert find_by_tag("nonexistent", path=tags_file) == []


def test_list_all(tags_file):
    add_tags(EXPR, ["work"], path=tags_file)
    add_tags(EXPR2, ["monitoring"], path=tags_file)
    all_entries = list_all(path=tags_file)
    assert len(all_entries) == 2


def test_delete_entry(tags_file):
    add_tags(EXPR, ["work"], path=tags_file)
    delete_entry(EXPR, path=tags_file)
    assert list_all(path=tags_file) == []


def test_delete_entry_nonexistent_is_noop(tags_file):
    delete_entry("0 0 * * *", path=tags_file)  # should not raise


def test_entry_serialisation_roundtrip():
    e = TagEntry(expression=EXPR, tags=["a", "b"], note="hi")
    assert TagEntry.from_dict(e.to_dict()) == e
