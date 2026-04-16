"""Tests for template_library and cli_template."""
import pytest
from unittest.mock import patch
from crontab_doctor.template_library import (
    list_templates, find_template, BUILTIN_TEMPLATES, Template
)


def test_builtin_templates_not_empty():
    assert len(BUILTIN_TEMPLATES) > 0


def test_all_templates_have_required_fields():
    for t in BUILTIN_TEMPLATES:
        assert t.name
        assert t.expression
        assert t.description


def test_find_template_existing():
    t = find_template("hourly")
    assert t is not None
    assert t.expression == "0 * * * *"


def test_find_template_missing_returns_none():
    assert find_template("does-not-exist") is None


def test_list_templates_no_filter_returns_all():
    assert list_templates() == BUILTIN_TEMPLATES


def test_list_templates_by_category():
    ops = list_templates(category="ops")
    assert all(t.category == "ops" for t in ops)
    assert len(ops) >= 1


def test_list_templates_by_tag():
    daily = list_templates(tag="daily")
    assert all("daily" in t.tags for t in daily)
    assert len(daily) >= 1


def test_list_templates_category_and_tag():
    results = list_templates(category="business", tag="weekday")
    assert all(t.category == "business" and "weekday" in t.tags for t in results)


def test_list_templates_unknown_category_empty():
    assert list_templates(category="nonexistent") == []


def test_template_to_dict():
    t = find_template("yearly")
    d = t.to_dict()
    assert d["name"] == "yearly"
    assert d["expression"] == "0 0 1 1 *"
    assert "tags" in d
    assert "category" in d


def test_template_repr():
    t = Template("test", "* * * * *", "desc")
    assert "test" in repr(t)
    assert "* * * * *" in repr(t)


def test_cmd_template_list(capsys):
    import argparse
    from crontab_doctor.cli_template import cmd_template
    args = argparse.Namespace(subcmd="list", category=None, tag=None, no_color=True)
    rc = cmd_template(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "hourly" in out
    assert "0 * * * *" in out


def test_cmd_template_show(capsys):
    import argparse
    from crontab_doctor.cli_template import cmd_template
    args = argparse.Namespace(subcmd="show", name="hourly")
    rc = cmd_template(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "0 * * * *" in out


def test_cmd_template_show_missing(capsys):
    import argparse
    from crontab_doctor.cli_template import cmd_template
    args = argparse.Namespace(subcmd="show", name="ghost")
    rc = cmd_template(args)
    assert rc == 1
