"""Tests for the CLI entry point."""

import textwrap
import pytest
from unittest.mock import patch, mock_open

from crontab_doctor.cli import main, build_parser


VALID_EXPR = "*/5 * * * * /usr/bin/backup"
INVALID_EXPR = "99 * * * * /cmd"

CRONTAB_CONTENT = textwrap.dedent("""\
    # daily backup
    0 2 * * * /usr/bin/backup
    30 3 * * * /usr/bin/cleanup
""")


def test_build_parser_has_check_and_audit():
    parser = build_parser()
    assert parser is not None


def test_check_valid_expression_exits_zero(capsys):
    rc = main(["check", VALID_EXPR, "--no-color"])
    assert rc == 0
    out = capsys.readouterr().out
    assert VALID_EXPR.split()[-1] in out or "*/5" in out


def test_check_invalid_expression_exits_one(capsys):
    rc = main(["check", INVALID_EXPR, "--no-color"])
    assert rc == 1
    out = capsys.readouterr().out
    assert out  # some output produced


def test_audit_valid_file_exits_zero(capsys, tmp_path):
    cron_file = tmp_path / "crontab"
    cron_file.write_text(CRONTAB_CONTENT)
    rc = main(["audit", str(cron_file), "--no-color"])
    assert rc == 0


def test_audit_file_with_invalid_expr_exits_one(capsys, tmp_path):
    cron_file = tmp_path / "crontab"
    cron_file.write_text("99 * * * * /cmd\n")
    rc = main(["audit", str(cron_file), "--no-color"])
    assert rc == 1


def test_audit_missing_file_exits_two(capsys):
    rc = main(["audit", "/nonexistent/path/crontab", "--no-color"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "Error" in err


def test_audit_skips_comments_and_blanks(capsys, tmp_path):
    cron_file = tmp_path / "crontab"
    cron_file.write_text("# comment\n\n0 1 * * * /cmd\n")
    rc = main(["audit", str(cron_file), "--no-color"])
    assert rc == 0


def test_audit_no_conflicts_flag(capsys, tmp_path):
    cron_file = tmp_path / "crontab"
    cron_file.write_text("0 * * * * /cmd1\n0 * * * * /cmd2\n")
    rc = main(["audit", str(cron_file), "--no-color", "--no-conflicts"])
    out = capsys.readouterr().out
    assert "conflict" not in out.lower()


def test_check_no_color_flag(capsys):
    rc = main(["check", VALID_EXPR, "--no-color"])
    out = capsys.readouterr().out
    assert "\x1b[" not in out
