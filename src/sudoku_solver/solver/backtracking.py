"""Backtracking solver (v1) with multi-solution detection (up to 2)."""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from sudoku_solver.board.grid import Grid
from sudoku_solver.trace.tracer import Tracer, TraceSink
from sudoku_solver.types import SolveResult, Stats
from sudoku_solver.instrumentation.recorder import Recorder
from sudoku_solver.metrics.collector import MetricsCollector
from sudoku_solver.strategies.base import CandidateMap, StrategyStep
from sudoku_solver.strategies.candidates import build_candidate_map
from sudoku_solver.strategies.policies import StrategyRunner, build_runner


class _Counter:
    def __init__(self) -> None:
        self.calls = 0
        self.assignments = 0
        self.backtracks = 0
        self.max_depth = 0



def _apply_strategy_step(
    grid: Grid,
    candidates: CandidateMap,
    step: StrategyStep,
    rec: Recorder,
    ctr: _Counter,
    deduced_stack: List[Tuple[int, int, int]],
    depth: int,
) -> tuple[bool, CandidateMap]:
    rec.strategy.step(step, depth)
    new_candidates = candidates
    # Apply eliminations first so assignments can leverage refreshed candidates
    for elim in step.eliminations:
        key = (elim.row, elim.col)
        cand = new_candidates.get(key)
        if not cand:
            continue
        removed = cand.intersection(elim.values)
        if not removed:
            continue
        cand.difference_update(removed)
        if not cand:
            rec.attempt.contradiction(elim.row, elim.col, None, reason="no_candidate", depth=depth)
            return False, new_candidates
    # Apply assignments
    for assignment in step.assignments:
        if grid.cells[assignment.row][assignment.col] != 0 and grid.cells[assignment.row][assignment.col] != assignment.value:
            rec.attempt.contradiction(assignment.row, assignment.col, assignment.value, reason="conflict", depth=depth)
            return False, new_candidates
        if not grid.is_valid_placement(assignment.row, assignment.col, assignment.value):
            rec.attempt.contradiction(
                assignment.row, assignment.col, assignment.value, reason="invalid_candidate", depth=depth
            )
            return False, new_candidates
        grid.set_cell(assignment.row, assignment.col, assignment.value)
        ctr.assignments += 1
        rec.attempt.assign(assignment.row, assignment.col, assignment.value, source="deduced", depth=depth)
        deduced_stack.append((assignment.row, assignment.col, assignment.value))
        new_candidates = build_candidate_map(grid)
    return True, new_candidates


def _apply_deductions(
    grid: Grid,
    rec: Recorder,
    ctr: _Counter,
    depth: int,
    deduced_stack: List[Tuple[int, int, int]],
    runner: StrategyRunner | None,
) -> tuple[bool, CandidateMap]:
    candidates = build_candidate_map(grid)
    if runner is None:
        return True, candidates
    while True:
        contradiction_cells = [(r, c) for (r, c), vals in candidates.items() if not vals]
        if contradiction_cells:
            for r, c in contradiction_cells:
                rec.attempt.contradiction(r, c, None, reason="no_candidate", depth=depth)
            return False, candidates

        step = runner.next_step(grid, candidates)
        if step is None:
            break
        ok, candidates = _apply_strategy_step(grid, candidates, step, rec, ctr, deduced_stack, depth)
        if not ok:
            return False, candidates
    return True, candidates


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
    runner: StrategyRunner | None,
) -> None:
    if len(solutions) >= max_solutions:
        return

    ctr.calls += 1
    ctr.max_depth = max(ctr.max_depth, depth)
    rec.search.update_depth(depth)

    deduced: List[Tuple[int, int, int]] = []
    candidates: CandidateMap | None = None
    if runner is not None:
        ok, candidates = _apply_deductions(grid, rec, ctr, depth, deduced, runner)
        if not ok:
            _revert_deductions(grid, rec, deduced, depth)
            return
    else:
        candidates = build_candidate_map(grid)

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
    values: Sequence[int]
    if candidates and (r, c) in candidates:
        values = sorted(candidates[(r, c)])
    else:
        values = list(range(1, 10))
    for v in values:
        if grid.is_valid_placement(r, c, v):
            grid.set_cell(r, c, v)
            ctr.assignments += 1
            rec.attempt.assign(r, c, v, source="guess", depth=depth)
            _search(grid, depth + 1, rec, ctr, solutions, max_solutions, runner)
            if len(solutions) >= max_solutions:
                grid.clear_cell(r, c)
                _revert_deductions(grid, rec, deduced, depth)
                return
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
    strategy_policy: str = "default",
    strategy_override: Optional[Sequence[str]] = None,
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
    runner: StrategyRunner | None = None
    if use_deductions:
        runner = build_runner(strategy_policy, strategy_override)
    _search(grid, 0, rec, ctr, solutions, max_solutions, runner)

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
