from __future__ import annotations

from sudoku_solver.board.grid import Grid
from sudoku_solver.strategies.base import StrategyContext
from sudoku_solver.strategies.claiming import ClaimingStrategy
from sudoku_solver.strategies.naked_pair import NakedPairStrategy
from sudoku_solver.strategies.naked_single import NakedSingleStrategy
from sudoku_solver.strategies.pointing import PointingStrategy
from sudoku_solver.strategies.policies import StrategyRunner


def _empty_grid() -> Grid:
    return Grid([[0 for _ in range(9)] for _ in range(9)])


def test_naked_single_returns_assignment() -> None:
    grid = _empty_grid()
    candidates = {
        (0, 0): {5},
        (0, 1): {1, 2},
    }
    step = NakedSingleStrategy().apply(StrategyContext(grid=grid, candidates=candidates))
    assert step is not None
    assert step.assignments[0].row == 0
    assert step.assignments[0].value == 5


def test_naked_pair_eliminates_other_cells() -> None:
    grid = _empty_grid()
    candidates = {
        (0, 0): {1, 2},
        (0, 1): {1, 2},
        (0, 2): {1, 2, 3},
    }
    step = NakedPairStrategy().apply(StrategyContext(grid=grid, candidates=candidates))
    assert step is not None
    assert step.eliminations
    assert step.eliminations[0].values == {1, 2}
    assert step.eliminations[0].col == 2


def test_pointing_strategy_targets_row_outside_box() -> None:
    grid = _empty_grid()
    candidates = {
        (0, 0): {5, 8},
        (0, 1): {5, 7},
        (0, 4): {5, 9},  # outside the top-left box
    }
    step = PointingStrategy().apply(StrategyContext(grid=grid, candidates=candidates))
    assert step is not None
    assert any(elim.col == 4 for elim in step.eliminations)


def test_claiming_strategy_eliminates_inside_box() -> None:
    grid = _empty_grid()
    candidates = {
        (0, 3): {4},
        (0, 4): {4},
        (1, 3): {4, 9},
        (1, 4): {4, 6},
        (2, 3): {4, 8},
    }
    step = ClaimingStrategy().apply(StrategyContext(grid=grid, candidates=candidates))
    assert step is not None
    assert any(elim.row == 1 and elim.col == 3 for elim in step.eliminations)


def test_strategy_runner_respects_order() -> None:
    grid = _empty_grid()
    candidates = {
        (0, 0): {1},
        (0, 1): {2},
    }
    runner = StrategyRunner(strategies=[NakedSingleStrategy(), PointingStrategy()])
    step = runner.next_step(grid, candidates)
    assert step is not None
    assert step.strategy == "naked_single"
