"""Backtracking solver (v1) with multi-solution detection (up to 2)."""

from __future__ import annotations

from typing import List

from sudoku_solver.board.grid import Grid
from sudoku_solver.trace.tracer import Tracer
from sudoku_solver.types import SolveResult, Stats


class _Counter:
    def __init__(self) -> None:
        self.calls = 0
        self.assignments = 0
        self.backtracks = 0
        self.max_depth = 0


def _search(grid: Grid, depth: int, tracer: Tracer, ctr: _Counter, solutions: List[List[List[int]]], max_solutions: int) -> None:
    if len(solutions) >= max_solutions:
        return

    ctr.calls += 1
    ctr.max_depth = max(ctr.max_depth, depth)

    empty = grid.first_empty()
    if empty is None:
        # Solution found
        solutions.append([row[:] for row in grid.cells])
        tracer.solution_found()
        return

    r, c = empty
    tracer.choose_cell(r, c, depth)
    for v in range(1, 10):
        if grid.is_valid_placement(r, c, v):
            grid.set_cell(r, c, v)
            ctr.assignments += 1
            tracer.assign(r, c, v, depth)
            _search(grid, depth + 1, tracer, ctr, solutions, max_solutions)
            if len(solutions) >= max_solutions:
                grid.clear_cell(r, c)
                return
            # backtrack
            grid.clear_cell(r, c)
            ctr.backtracks += 1
            tracer.unassign(r, c, v, depth)
        else:
            tracer.contradiction(r, c, depth, reason="invalid_candidate")


def solve_backtracking(grid: Grid, trace_enabled: bool = False, trace_summary: bool = False, max_solutions: int = 2) -> SolveResult:
    """Solve a Sudoku using DFS backtracking and detect up to 2 solutions."""
    mode = "summary" if (trace_enabled and trace_summary) else "steps"
    if grid.givens_conflict():
        # No solutions if givens already conflict
        stats = Stats(calls=0, assignments=0, backtracks=0, max_depth=0)
        tracer = Tracer(enabled=trace_enabled, mode=mode)
        return SolveResult(status="unsat", solution=None, stats=stats, trace=tracer.to_json_obj())

    tracer = Tracer(enabled=trace_enabled, mode=mode)
    ctr = _Counter()
    solutions: List[List[List[int]]] = []
    _search(grid, 0, tracer, ctr, solutions, max_solutions)

    if len(solutions) == 0:
        status = "unsat"
        solution = None
    elif len(solutions) == 1:
        status = "unique"
        solution = solutions[0]
    else:
        status = "multiple"
        solution = solutions[0]

    stats = Stats(calls=ctr.calls, assignments=ctr.assignments, backtracks=ctr.backtracks, max_depth=ctr.max_depth)
    return SolveResult(status=status, solution=solution, stats=stats, trace=tracer.to_json_obj())
