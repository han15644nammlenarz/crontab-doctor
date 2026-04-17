"""Tests for crontab_doctor.cron_heatmap."""
import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from crontab_doctor.cron_heatmap import build_heatmap, HeatmapResult, DAYS, HOURS


FIXED_NOW = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)  # Monday


def test_heatmap_result_ok_when_no_error():
    r = HeatmapResult(expression="* * * * *", error=None, grid={})
    assert r.ok is True


def test_heatmap_result_not_ok_when_error():
    r = HeatmapResult(expression="bad", error="parse error", grid={})
    assert r.ok is False


def test_heatmap_summary_error():
    r = HeatmapResult(expression="bad", error="oops", grid={})
    assert "oops" in r.summary()
    assert "bad" in r.summary()


def test_heatmap_summary_ok():
    grid = {d: {h: 0 for h in HOURS} for d in range(7)}
    grid[0][9] = 3
    r = HeatmapResult(expression="0 9 * * *", error=None, grid=grid)
    assert "3" in r.summary()


def test_build_heatmap_invalid_expression():
    result = build_heatmap("not a cron")
    assert not result.ok
    assert result.error is not None


def test_build_heatmap_every_minute_populates_grid():
    result = build_heatmap("* * * * *", days_ahead=1)
    assert result.ok
    assert set(result.grid.keys()) == set(range(7))
    total = sum(v for row in result.grid.values() for v in row.values())
    assert total > 0


def test_build_heatmap_daily_at_noon_concentrates_in_one_hour():
    result = build_heatmap("0 12 * * *", days_ahead=7)
    assert result.ok
    noon_total = sum(result.grid[d][12] for d in range(7))
    other_total = sum(
        result.grid[d][h] for d in range(7) for h in HOURS if h != 12
    )
    assert noon_total > 0
    assert other_total == 0


def test_build_heatmap_grid_has_all_days_and_hours():
    result = build_heatmap("0 * * * *", days_ahead=3)
    assert result.ok
    assert len(result.grid) == 7
    for day_row in result.grid.values():
        assert len(day_row) == 24


def test_build_heatmap_next_runs_exception_returns_error():
    with patch("crontab_doctor.cron_heatmap.next_runs", side_effect=RuntimeError("fail")):
        result = build_heatmap("* * * * *", days_ahead=1)
    assert not result.ok
    assert "fail" in result.error
