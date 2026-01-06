"""Strategy interfaces and shared dataclasses for deduction policies."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Protocol, Sequence, Set, Tuple

from sudoku_solver.board.grid import Grid

Coord = Tuple[int, int]
CandidateMap = Dict[Coord, Set[int]]


ROW_UNITS: List[List[Coord]] = [[(r, c) for c in range(9)] for r in range(9)]
COLUMN_UNITS: List[List[Coord]] = [[(r, c) for r in range(9)] for c in range(9)]
BOX_UNITS: List[List[Coord]] = [
    [(r, c) for r in range(br, br + 3) for c in range(bc, bc + 3)]
    for br in range(0, 9, 3)
    for bc in range(0, 9, 3)
]
ALL_UNITS: List[List[Coord]] = ROW_UNITS + COLUMN_UNITS + BOX_UNITS


@dataclass
class AssignmentAction:
    row: int
    col: int
    value: int
    reason: str
    note: Optional[str] = None


@dataclass
class EliminationAction:
    row: int
    col: int
    values: Set[int]
    reason: str
    note: Optional[str] = None


@dataclass
class StrategyStep:
    strategy: str
    description: str
    assignments: List[AssignmentAction] = field(default_factory=list)
    eliminations: List[EliminationAction] = field(default_factory=list)
    metadata: Dict[str, object] | None = None


@dataclass
class StrategyContext:
    grid: Grid
    candidates: CandidateMap


class Strategy(Protocol):
    """Strategy implementation contract."""

    name: str

    def apply(self, ctx: StrategyContext) -> StrategyStep | None:
        ...


@dataclass(frozen=True)
class StrategyPolicy:
    name: str
    strategies: Sequence[str]
    description: str
