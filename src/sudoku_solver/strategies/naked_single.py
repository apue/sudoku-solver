"""Naked single strategy."""
from __future__ import annotations

from sudoku_solver.strategies.base import AssignmentAction, Strategy, StrategyContext, StrategyStep


class NakedSingleStrategy(Strategy):
    name = "naked_single"

    def apply(self, ctx: StrategyContext) -> StrategyStep | None:
        for (r, c), values in ctx.candidates.items():
            if len(values) == 1:
                value = next(iter(values))
                return StrategyStep(
                    strategy=self.name,
                    description=f"r{r + 1}c{c + 1} 仅剩 {value}",
                    assignments=[AssignmentAction(row=r, col=c, value=value, reason="only_candidate")],
                )
        return None
