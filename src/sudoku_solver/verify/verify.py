"""Verify a solved grid meets Sudoku constraints and respects givens."""

from __future__ import annotations

from typing import List

from sudoku_solver.board.grid import Grid


def _valid_full_solution(grid: List[List[int]]) -> bool:
    # Check rows
    for r in range(9):
        row = grid[r]
        if sorted(row) != list(range(1, 10)):
            return False
    # Check columns
    for c in range(9):
        col = [grid[r][c] for r in range(9)]
        if sorted(col) != list(range(1, 10)):
            return False
    # Check boxes
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box = [grid[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)]
            if sorted(box) != list(range(1, 10)):
                return False
    return True


def verify_solution_respects_givens(puzzle: Grid, solution: List[List[int]]) -> bool:
    for r in range(9):
        for c in range(9):
            given = puzzle.cells[r][c]
            if given != 0 and solution[r][c] != given:
                return False
    return True


def verify(puzzle: Grid, solution: List[List[int]]) -> bool:
    """Return True if `solution` is a valid Sudoku solution for `puzzle`."""
    if not _valid_full_solution(solution):
        return False
    return verify_solution_respects_givens(puzzle, solution)

