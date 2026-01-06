"""Strategy registry and runner."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from sudoku_solver.board.grid import Grid
from sudoku_solver.strategies.base import CandidateMap, Strategy, StrategyContext, StrategyPolicy, StrategyStep
from sudoku_solver.strategies.claiming import ClaimingStrategy
from sudoku_solver.strategies.hidden_single import HiddenSingleStrategy
from sudoku_solver.strategies.naked_pair import NakedPairStrategy
from sudoku_solver.strategies.naked_single import NakedSingleStrategy
from sudoku_solver.strategies.pointing import PointingStrategy


@dataclass
class StrategyRunner:
    strategies: Sequence[Strategy]

    def next_step(self, grid: Grid, candidates: CandidateMap) -> StrategyStep | None:
        ctx = StrategyContext(grid=grid, candidates=candidates)
        for strategy in self.strategies:
            step = strategy.apply(ctx)
            if step:
                return step
        return None


_STRATEGY_BUILDERS: Dict[str, Strategy] = {
    "naked_single": NakedSingleStrategy(),
    "hidden_single": HiddenSingleStrategy(),
    "naked_pair": NakedPairStrategy(),
    "pointing": PointingStrategy(),
    "claiming": ClaimingStrategy(),
}

AVAILABLE_POLICIES: Dict[str, StrategyPolicy] = {
    "human-lite": StrategyPolicy(
        name="human-lite",
        strategies=("naked_single", "hidden_single"),
        description="仅单值推理",
    ),
    "default": StrategyPolicy(
        name="default",
        strategies=("naked_single", "hidden_single", "naked_pair", "pointing", "claiming"),
        description="单值 + pair/pointing/claiming",
    ),
    "aggressive": StrategyPolicy(
        name="aggressive",
        strategies=("naked_single", "hidden_single", "naked_pair", "pointing", "claiming"),
        description="与 default 相同（预留更复杂策略）",
    ),
}


def _instantiate(names: Sequence[str]) -> List[Strategy]:
    seen: Dict[str, bool] = {}
    ordered: List[Strategy] = []
    for name in names:
        if name in seen:
            continue
        strategy = _STRATEGY_BUILDERS.get(name)
        if not strategy:
            raise ValueError(f"未知策略：{name}")
        ordered.append(strategy)
        seen[name] = True
    return ordered


def build_runner(policy_name: str, override: Sequence[str] | None = None) -> StrategyRunner:
    override_list = list(override) if override is not None else None
    if override_list is not None and len(override_list) == 0:
        raise ValueError("策略覆盖列表不能为空")
    policy = AVAILABLE_POLICIES.get(policy_name)
    if not policy:
        raise ValueError(f"未知 policy：{policy_name}")
    names = override_list if override_list is not None else list(policy.strategies)
    strategies = _instantiate(names)
    return StrategyRunner(strategies=strategies)
