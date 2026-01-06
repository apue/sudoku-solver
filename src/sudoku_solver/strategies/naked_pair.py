"""Naked pair strategy."""
from __future__ import annotations

from collections import defaultdict

from sudoku_solver.strategies.base import ALL_UNITS, EliminationAction, Strategy, StrategyContext, StrategyStep


class NakedPairStrategy(Strategy):
    name = "naked_pair"

    def apply(self, ctx: StrategyContext) -> StrategyStep | None:
        for unit in ALL_UNITS:
            pairs = defaultdict(list)
            for coord in unit:
                values = ctx.candidates.get(coord)
                if values and len(values) == 2:
                    key = tuple(sorted(values))
                    pairs[key].append(coord)
            for values, cells in pairs.items():
                if len(cells) != 2:
                    continue
                eliminations = []
                target_values = set(values)
                for r, c in unit:
                    if (r, c) in cells:
                        continue
                    cand = ctx.candidates.get((r, c))
                    if not cand:
                        continue
                    remove = cand.intersection(target_values)
                    if remove:
                        eliminations.append(
                            EliminationAction(row=r, col=c, values=set(remove), reason="naked_pair"),
                        )
                if eliminations:
                    coords = ", ".join([f"r{r + 1}c{c + 1}" for r, c in cells])
                    description = f"{coords} 构成裸对 {target_values}"
                    return StrategyStep(
                        strategy=self.name,
                        description=description,
                        eliminations=eliminations,
                    )
        return None
