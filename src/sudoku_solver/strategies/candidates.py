"""Candidate map helpers for strategies and solver."""
from __future__ import annotations

from typing import Dict, Set, Tuple

from sudoku_solver.board.grid import Grid

Coord = Tuple[int, int]
CandidateMap = Dict[Coord, Set[int]]


def build_candidate_map(grid: Grid) -> CandidateMap:
    candidates: CandidateMap = {}
    for r in range(9):
        for c in range(9):
            if grid.cells[r][c] != 0:
                continue
            allowed = {v for v in range(1, 10) if grid.is_valid_placement(r, c, v)}
            candidates[(r, c)] = allowed
    return candidates
