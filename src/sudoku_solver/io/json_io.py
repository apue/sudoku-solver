"""JSON I/O contract helpers for v1."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sudoku_solver.board.grid import Grid


def load_puzzle(path: str | Path) -> Grid:
    """Load and validate a puzzle JSON into a Grid.

    Raises ValueError with a Chinese message on contract violations.
    """
    try:
        obj = json.loads(Path(path).read_text())
    except Exception as e:  # noqa: BLE001
        raise ValueError(f"无法读取 JSON：{e}") from e

    if not isinstance(obj, dict) or "grid" not in obj:
        raise ValueError("输入必须包含 grid 字段")
    grid = obj["grid"]
    if not (isinstance(grid, list) and len(grid) == 9 and all(isinstance(r, list) and len(r) == 9 for r in grid)):
        raise ValueError("grid 必须为 9x9 数组")
    try:
        g = Grid([[int(v) for v in row] for row in grid])
    except Exception as e:  # noqa: BLE001
        raise ValueError(str(e))
    if g.givens_conflict():
        raise ValueError("givens 冲突：不满足行/列/宫约束")
    return g


def dump_result(obj: Dict[str, Any], path: str | Path) -> None:
    """Write result JSON to a file using UTF-8 without ASCII escaping."""
    Path(path).write_text(json.dumps(obj, ensure_ascii=False))


def load_solution_grid(path: str | Path) -> List[List[int]]:
    """Load solution JSON with format: { "grid": [[...9], ... 9] }"""
    try:
        obj = json.loads(Path(path).read_text())
    except Exception as e:  # noqa: BLE001
        raise ValueError(f"无法读取 JSON：{e}") from e
    if not isinstance(obj, dict) or "grid" not in obj:
        raise ValueError("solution 文件必须包含 grid 字段")
    grid = obj["grid"]
    if not (isinstance(grid, list) and len(grid) == 9 and all(isinstance(r, list) and len(r) == 9 for r in grid)):
        raise ValueError("solution.grid 必须为 9x9 数组")
    for r in range(9):
        for c in range(9):
            v = grid[r][c]
            if not isinstance(v, int) or not (1 <= v <= 9):
                raise ValueError("solution.grid 元素必须为 1..9 的整数")
    return grid
