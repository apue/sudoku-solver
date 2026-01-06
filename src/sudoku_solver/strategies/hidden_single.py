"""Hidden single strategy for rows/columns/boxes."""
from __future__ import annotations

from collections import defaultdict

from sudoku_solver.strategies.base import ALL_UNITS, AssignmentAction, Strategy, StrategyContext, StrategyStep


class HiddenSingleStrategy(Strategy):
    name = "hidden_single"

    def apply(self, ctx: StrategyContext) -> StrategyStep | None:
        for unit in ALL_UNITS:
            locations = defaultdict(list)
            for r, c in unit:
                vals = ctx.candidates.get((r, c))
                if not vals:
                    continue
                for value in vals:
                    locations[value].append((r, c))
            for value, cells in locations.items():
                if len(cells) == 1:
                    r, c = cells[0]
                    return StrategyStep(
                        strategy=self.name,
                        description=f"{self._unit_label(unit)} 中 {value} 仅可放在 r{r + 1}c{c + 1}",
                        assignments=[AssignmentAction(row=r, col=c, value=value, reason="unit_unique")],
                    )
        return None

    @staticmethod
    def _unit_label(unit: list[tuple[int, int]]) -> str:
        r0, c0 = unit[0]
        if len(unit) == 9 and r0 == unit[-1][0]:
            return f"第 {r0 + 1} 行"
        if len(unit) == 9 and c0 == unit[-1][1]:
            return f"第 {c0 + 1} 列"
        br = (r0 // 3) + 1
        bc = (c0 // 3) + 1
        return f"第 {br},{bc} 宫"
