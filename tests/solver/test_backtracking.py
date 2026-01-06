from __future__ import annotations

import json
from pathlib import Path

from sudoku_solver.board.grid import Grid
from sudoku_solver.io.json_io import load_puzzle
from sudoku_solver.solver.backtracking import solve_backtracking
from sudoku_solver.verify.verify import verify as verify_solution


def test_solve_unique_returns_valid_solution(positive_puzzle_path: Path) -> None:
    grid = load_puzzle(positive_puzzle_path)
    result, metrics = solve_backtracking(grid)
    assert result.status == "unique"
    assert result.solution is not None
    assert verify_solution(grid, result.solution)
    assert metrics["status"] == "unique"
    assert metrics["solutions_found"] >= 1


def test_solve_unsat_on_conflict_input(conflict_puzzle_path: Path) -> None:
    payload = json.loads(conflict_puzzle_path.read_text())
    grid = Grid(payload["grid"])
    result, metrics = solve_backtracking(grid)
    assert result.status == "unsat"
    assert result.solution is None
    assert result.stats.calls == 0
    assert metrics["status"] == "unsat"


def test_trace_summary_mode_only(positive_puzzle_path: Path) -> None:
    grid = load_puzzle(positive_puzzle_path)
    result, _ = solve_backtracking(grid, trace_enabled=True, trace_mode="summary")
    assert result.trace is not None
    assert result.trace["mode"] == "summary"
    assert "counts" in result.trace


def test_deductions_emit_metrics(positive_puzzle_path: Path) -> None:
    grid = load_puzzle(positive_puzzle_path)
    _, metrics = solve_backtracking(grid, use_deductions=True)
    assert metrics["deduced_assignments"] > 0


def test_no_deductions_can_be_disabled(positive_puzzle_path: Path) -> None:
    grid = load_puzzle(positive_puzzle_path)
    _, metrics = solve_backtracking(grid, use_deductions=False)
    assert metrics["deduced_assignments"] == 0
