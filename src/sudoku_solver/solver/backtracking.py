"""Backtracking solver (v1) with multi-solution detection (up to 2)."""

from __future__ import annotations

from typing import List

from sudoku_solver.board.grid import Grid
from sudoku_solver.trace.tracer import Tracer, TraceSink
from sudoku_solver.types import SolveResult, Stats
from sudoku_solver.instrumentation.recorder import Recorder
from sudoku_solver.metrics.collector import MetricsCollector


class _Counter:
    def __init__(self) -> None:
        self.calls = 0
        self.assignments = 0
        self.backtracks = 0
        self.max_depth = 0


def _search(grid: Grid, depth: int, rec: Recorder, ctr: _Counter, solutions: List[List[List[int]]], max_solutions: int) -> None:
    if len(solutions) >= max_solutions:
        return

    ctr.calls += 1
    ctr.max_depth = max(ctr.max_depth, depth)
    rec.search.update_depth(depth)

    empty = grid.first_empty()
    if empty is None:
        # Solution found
        solutions.append([row[:] for row in grid.cells])
        rec.result.solution_found()
        return

    r, c = empty
    rec.decision.choose_cell(r, c, depth)
    rec.decision.guess_point(depth)
    for v in range(1, 10):
        if grid.is_valid_placement(r, c, v):
            grid.set_cell(r, c, v)
            ctr.assignments += 1
            rec.attempt.assign(r, c, v, source="guess", depth=depth)
            _search(grid, depth + 1, rec, ctr, solutions, max_solutions)
            if len(solutions) >= max_solutions:
                grid.clear_cell(r, c)
                return
            # backtrack
            grid.clear_cell(r, c)
            ctr.backtracks += 1
            rec.state.unassign(r, c, v, reason="backtrack", depth=depth)
        else:
            rec.attempt.contradiction(r, c, v, reason="invalid_candidate", depth=depth)


def solve_backtracking(grid: Grid, trace_enabled: bool = False, trace_summary: bool = False, max_solutions: int = 2):
    """Solve a Sudoku using DFS backtracking and detect up to 2 solutions."""
    mode = "summary" if (trace_enabled and trace_summary) else "steps"
    if grid.givens_conflict():
        # No solutions if givens already conflict
        stats = Stats(calls=0, assignments=0, backtracks=0, max_depth=0)
        tracer = Tracer(enabled=trace_enabled, mode=mode)
        metrics = MetricsCollector()
        return SolveResult(status="unsat", solution=None, stats=stats, trace=tracer.to_json_obj()), metrics.finalize("unsat")

    tracer = Tracer(enabled=trace_enabled, mode=mode)
    trace_sink = TraceSink(tracer)
    metrics = MetricsCollector()
    rec = Recorder([metrics, trace_sink])
    ctr = _Counter()
    solutions: List[List[List[int]]] = []
    _search(grid, 0, rec, ctr, solutions, max_solutions)

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
    metrics_dict = metrics.finalize(status)
    # Attach metrics in CLI layer; return alongside result
    return SolveResult(status=status, solution=solution, stats=stats, trace=tracer.to_json_obj()), metrics_dict
