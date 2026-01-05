from __future__ import annotations

import json
from pathlib import Path

import pytest

from sudoku_solver.board.grid import Grid


def _load_grid(path: Path) -> Grid:
    data = json.loads(path.read_text())
    return Grid(data["grid"])


def test_grid_accepts_valid_shape(positive_puzzle_path: Path) -> None:
    grid = _load_grid(positive_puzzle_path)
    assert isinstance(grid, Grid)


def test_grid_rejects_invalid_shape() -> None:
    with pytest.raises(ValueError):
        Grid([[0] * 8 for _ in range(9)])


def test_is_valid_placement_rejects_duplicates() -> None:
    grid = Grid([[0] * 9 for _ in range(9)])
    grid.set_cell(0, 0, 5)
    assert not grid.is_valid_placement(0, 1, 5)
    assert grid.is_valid_placement(0, 1, 6)


def test_givens_conflict_detects_issue(conflict_puzzle_path: Path) -> None:
    grid = _load_grid(conflict_puzzle_path)
    assert grid.givens_conflict() is True
