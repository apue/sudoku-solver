"""Backtracking solver (v1) with multi-solution detection (up to 2)."""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

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


Coord = Tuple[int, int]


def _build_candidates(grid: Grid) -> Dict[Coord, Set[int]]:
    candidates: Dict[Coord, Set[int]] = {}
    for r in range(9):
        for c in range(9):
            if grid.cells[r][c] != 0:
                continue
            allowed = {v for v in range(1, 10) if grid.is_valid_placement(r, c, v)}
            candidates[(r, c)] = allowed
    return candidates


def _units() -> List[List[Coord]]:
    units: List[List[Coord]] = []
    # Rows
    for r in range(9):
        units.append([(r, c) for c in range(9)])
    # Columns
    for c in range(9):
        units.append([(r, c) for r in range(9)])
    # Boxes
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            units.append([(r, c) for r in range(br, br + 3) for c in range(bc, bc + 3)])
    return units


UNITS = _units()


def _apply_deductions(grid: Grid, rec: Recorder, ctr: _Counter, depth: int, deduced_stack: List[Tuple[int, int, int]]) -> bool:
    while True:
        candidates = _build_candidates(grid)
        contradiction_cells = [(r, c) for (r, c), vals in candidates.items() if not vals]
        if contradiction_cells:
            for r, c in contradiction_cells:
                rec.attempt.contradiction(r, c, None, reason="no_candidate", depth=depth)
            return False

        progress = False
        # Naked singles
        singles = [((r, c), next(iter(vals))) for (r, c), vals in candidates.items() if len(vals) == 1]
        for (r, c), value in singles:
            grid.set_cell(r, c, value)
            ctr.assignments += 1
            rec.attempt.assign(r, c, value, source="deduced", depth=depth)
            deduced_stack.append((r, c, value))
            progress = True

        if progress:
            continue

        # Hidden singles
        for unit in UNITS:
            appearance: Dict[int, List[Coord]] = {}
            for r, c in unit:
                if grid.cells[r][c] != 0:
                    continue
                vals = candidates.get((r, c))
                if not vals:
                    continue
                for v in vals:
                    appearance.setdefault(v, []).append((r, c))
            hidden_found = False
            for value, cells in appearance.items():
                if len(cells) == 1:
                    r, c = cells[0]
                    grid.set_cell(r, c, value)
                    ctr.assignments += 1
                    rec.attempt.assign(r, c, value, source="deduced", depth=depth)
                    deduced_stack.append((r, c, value))
                    hidden_found = True
                    progress = True
                    break
            if hidden_found:
                break

        if not progress:
            break

    return True


def _revert_deductions(grid: Grid, rec: Recorder, deduced_stack: List[Tuple[int, int, int]], depth: int) -> None:
    while deduced_stack:
        r, c, value = deduced_stack.pop()
        grid.clear_cell(r, c)
        rec.state.unassign(r, c, value, reason="deduced_revert", depth=depth)


def _full_solution_valid(grid: Grid) -> bool:
    target = list(range(1, 10))
    for r in range(9):
        if sorted(grid.cells[r]) != target:
            return False
    for c in range(9):
        col = [grid.cells[r][c] for r in range(9)]
        if sorted(col) != target:
            return False
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box = [grid.cells[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)]
            if sorted(box) != target:
                return False
    return True


def _search(
    grid: Grid,
    depth: int,
    rec: Recorder,
    ctr: _Counter,
    solutions: List[List[List[int]]],
    max_solutions: int,
    use_deductions: bool,
) -> None:
    if len(solutions) >= max_solutions:
        return

    ctr.calls += 1
    ctr.max_depth = max(ctr.max_depth, depth)
    rec.search.update_depth(depth)

    deduced: List[Tuple[int, int, int]] = []
    if use_deductions:
        if not _apply_deductions(grid, rec, ctr, depth, deduced):
            _revert_deductions(grid, rec, deduced, depth)
            return

    empty = grid.first_empty()
    if empty is None:
        if _full_solution_valid(grid):
            solutions.append([row[:] for row in grid.cells])
            rec.result.solution_found()
        else:
            rec.attempt.contradiction(0, 0, None, reason="invalid_completion", depth=depth)
        _revert_deductions(grid, rec, deduced, depth)
        return

    r, c = empty
    rec.decision.choose_cell(r, c, depth)
    rec.decision.guess_point(depth)
    for v in range(1, 10):
        if grid.is_valid_placement(r, c, v):
            grid.set_cell(r, c, v)
            ctr.assignments += 1
            rec.attempt.assign(r, c, v, source="guess", depth=depth)
            _search(grid, depth + 1, rec, ctr, solutions, max_solutions, use_deductions)
            if len(solutions) >= max_solutions:
                grid.clear_cell(r, c)
                _revert_deductions(grid, rec, deduced, depth)
                return
            # backtrack
            grid.clear_cell(r, c)
            ctr.backtracks += 1
            rec.state.unassign(r, c, v, reason="backtrack", depth=depth)
        else:
            rec.attempt.contradiction(r, c, v, reason="invalid_candidate", depth=depth)

    _revert_deductions(grid, rec, deduced, depth)


def solve_backtracking(
    grid: Grid,
    trace_enabled: bool = False,
    trace_mode: str = "summary",
    max_solutions: int = 2,
    use_deductions: bool = True,
):
    """Solve a Sudoku using DFS backtracking and detect up to 2 solutions."""
    if grid.givens_conflict():
        # No solutions if givens already conflict
        stats = Stats(calls=0, assignments=0, backtracks=0, max_depth=0)
        tracer = Tracer(enabled=trace_enabled, mode=trace_mode)
        metrics = MetricsCollector()
        return SolveResult(status="unsat", solution=None, stats=stats, trace=tracer.to_json_obj()), metrics.finalize("unsat")

    tracer = Tracer(enabled=trace_enabled, mode=trace_mode)
    trace_sink = TraceSink(tracer)
    metrics = MetricsCollector()
    rec = Recorder([metrics, trace_sink])
    ctr = _Counter()
    solutions: List[List[List[int]]] = []
    _search(grid, 0, rec, ctr, solutions, max_solutions, use_deductions)

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
