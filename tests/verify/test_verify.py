from __future__ import annotations

from pathlib import Path

from sudoku_solver.io.json_io import load_puzzle, load_solution_grid
from sudoku_solver.verify import verify as verify_module


def test_verify_accepts_valid_solution(example_puzzle_path: Path, example_solution_path: Path) -> None:
    puzzle = load_puzzle(example_puzzle_path)
    solution = load_solution_grid(example_solution_path)
    assert verify_module.verify(puzzle, solution)


def test_verify_rejects_solution_breaking_givens(example_puzzle_path: Path, example_solution_path: Path) -> None:
    puzzle = load_puzzle(example_puzzle_path)
    solution = load_solution_grid(example_solution_path)
    solution[0][0] = (solution[0][0] % 9) + 1
    assert verify_module.verify(puzzle, solution) is False
