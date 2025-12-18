"""Grid representation and helpers for a 9x9 Sudoku."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


Coord = Tuple[int, int]  # (row, col), 0-based


@dataclass
class Grid:
    """9x9 grid with basic helpers and validation.

    Cells contain integers 0..9; 0 means empty.
    """

    cells: List[List[int]]

    def __post_init__(self) -> None:
        if len(self.cells) != 9 or any(len(r) != 9 for r in self.cells):
            raise ValueError("网格必须为 9x9")
        for r in range(9):
            for c in range(9):
                v = self.cells[r][c]
                if not isinstance(v, int) or v < 0 or v > 9:
                    raise ValueError("网格元素必须为 0..9 的整数")

    def clone(self) -> Grid:
        return Grid([row[:] for row in self.cells])

    def is_valid_placement(self, r: int, c: int, v: int) -> bool:
        """Check row/col/box constraints for placing v at (r,c)."""
        # Row
        if any(self.cells[r][cc] == v for cc in range(9)):
            return False
        # Column
        if any(self.cells[rr][c] == v for rr in range(9)):
            return False
        # Box
        br, bc = (r // 3) * 3, (c // 3) * 3
        for rr in range(br, br + 3):
            for cc in range(bc, bc + 3):
                if self.cells[rr][cc] == v:
                    return False
        return True

    def first_empty(self) -> Optional[Coord]:
        for r in range(9):
            for c in range(9):
                if self.cells[r][c] == 0:
                    return (r, c)
        return None

    def givens_conflict(self) -> bool:
        """Return True if givens (non-zero entries) already violate constraints."""
        for r in range(9):
            for c in range(9):
                v = self.cells[r][c]
                if v == 0:
                    continue
                # Temporarily clear and re-check to avoid self-conflict
                self.cells[r][c] = 0
                ok = self.is_valid_placement(r, c, v)
                self.cells[r][c] = v
                if not ok:
                    return True
        return False

    def set_cell(self, r: int, c: int, v: int) -> None:
        self.cells[r][c] = v

    def clear_cell(self, r: int, c: int) -> None:
        self.cells[r][c] = 0

    def __iter__(self) -> Iterable[List[int]]:
        return iter(self.cells)

