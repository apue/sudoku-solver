"""Claiming pair/triple strategy (row/column claims a box)."""
from __future__ import annotations

from collections import defaultdict

from sudoku_solver.strategies.base import COLUMN_UNITS, ROW_UNITS, EliminationAction, Strategy, StrategyContext, StrategyStep


class ClaimingStrategy(Strategy):
    name = "claiming"

    def apply(self, ctx: StrategyContext) -> StrategyStep | None:
        for unit_type, units in (("row", ROW_UNITS), ("col", COLUMN_UNITS)):
            for unit in units:
                by_value = defaultdict(list)
                for r, c in unit:
                    vals = ctx.candidates.get((r, c))
                    if not vals:
                        continue
                    for value in vals:
                        by_value[value].append((r, c))
                for value, cells in by_value.items():
                    if len(cells) < 2:
                        continue
                    boxes = {((r // 3), (c // 3)) for r, c in cells}
                    if len(boxes) != 1:
                        continue
                    box_r, box_c = next(iter(boxes))
                    eliminations = []
                    for rr in range(box_r * 3, box_r * 3 + 3):
                        for cc in range(box_c * 3, box_c * 3 + 3):
                            if unit_type == "row" and rr == unit[0][0]:
                                continue
                            if unit_type == "col" and cc == unit[0][1]:
                                continue
                            if (rr, cc) in cells:
                                continue
                            cand = ctx.candidates.get((rr, cc))
                            if cand and value in cand:
                                eliminations.append(
                                    EliminationAction(row=rr, col=cc, values={value}, reason=f"claiming_{unit_type}"),
                                )
                    if eliminations:
                        coords = ", ".join([f"r{r + 1}c{c + 1}" for r, c in cells])
                        description = f"{coords} 将 {value} 限定到同一宫"
                        return StrategyStep(
                            strategy=self.name,
                            description=description,
                            eliminations=eliminations,
                            metadata={"value": value, "unit": unit_type},
                        )
        return None
