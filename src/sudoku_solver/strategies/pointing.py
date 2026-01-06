"""Pointing pair/triple strategy."""
from __future__ import annotations

from collections import defaultdict

from sudoku_solver.strategies.base import BOX_UNITS, EliminationAction, Strategy, StrategyContext, StrategyStep


class PointingStrategy(Strategy):
    name = "pointing"

    def apply(self, ctx: StrategyContext) -> StrategyStep | None:
        for box in BOX_UNITS:
            by_value = defaultdict(list)
            for r, c in box:
                vals = ctx.candidates.get((r, c))
                if not vals:
                    continue
                for value in vals:
                    by_value[value].append((r, c))
            for value, cells in by_value.items():
                if len(cells) < 2:
                    continue
                eliminations = []
                rows = {r for r, _ in cells}
                cols = {c for _, c in cells}
                if len(rows) == 1:
                    row = next(iter(rows))
                    for c in range(9):
                        if (row, c) in box:
                            continue
                        cand = ctx.candidates.get((row, c))
                        if cand and value in cand:
                            eliminations.append(
                                EliminationAction(row=row, col=c, values={value}, reason="pointing_row"),
                            )
                elif len(cols) == 1:
                    col = next(iter(cols))
                    for r in range(9):
                        if (r, col) in box:
                            continue
                        cand = ctx.candidates.get((r, col))
                        if cand and value in cand:
                            eliminations.append(
                                EliminationAction(row=r, col=col, values={value}, reason="pointing_col"),
                            )
                if eliminations:
                    cells_label = ", ".join([f"r{r + 1}c{c + 1}" for r, c in cells])
                    description = f"{cells_label} 限制 {value} 只能沿行/列延伸"
                    return StrategyStep(
                        strategy=self.name,
                        description=description,
                        eliminations=eliminations,
                        metadata={"value": value},
                    )
        return None
