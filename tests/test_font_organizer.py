"""Tests for empty-directory cleanup in the font organizer."""

from __future__ import annotations

from pathlib import Path

from foundrytools_cli.commands.utils.font_organizer import (
    _remove_empty_directories,
)


def test_stops_at_boundary(tmp_path: Path) -> None:
    root = tmp_path / "input"
    nested = root / "a" / "b"
    nested.mkdir(parents=True)
    _remove_empty_directories(nested, stop_at=root)
    assert root.is_dir()
    assert not nested.exists()


def test_missing_directory_is_noop(tmp_path: Path) -> None:
    _remove_empty_directories(tmp_path / "gone", stop_at=tmp_path)
    assert tmp_path.is_dir()
