from __future__ import annotations

import json
from pathlib import Path

import pytest

from sudoku_solver.io import json_io


def test_load_puzzle_returns_grid(positive_puzzle_path: Path) -> None:
    grid = json_io.load_puzzle(positive_puzzle_path)
    assert grid.first_empty() is not None


def test_load_puzzle_rejects_conflict(conflict_puzzle_path: Path) -> None:
    with pytest.raises(ValueError):
        json_io.load_puzzle(conflict_puzzle_path)


def test_load_solution_grid_validates_values(tmp_path: Path) -> None:
    sol_path = tmp_path / "sol.json"
    sol_path.write_text(json.dumps({"grid": [[1] * 9 for _ in range(9)]}))
    grid = json_io.load_solution_grid(sol_path)
    assert grid[0][0] == 1

    sol_path.write_text(json.dumps({"grid": [[0] * 9 for _ in range(9)]}))
    with pytest.raises(ValueError):
        json_io.load_solution_grid(sol_path)


def test_dump_result_writes_json(tmp_path: Path) -> None:
    out = tmp_path / "out.json"
    json_io.dump_result({"status": "unique"}, out)
    data = json.loads(out.read_text())
    assert data["status"] == "unique"
