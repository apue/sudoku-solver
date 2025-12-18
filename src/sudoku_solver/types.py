"""Shared types for the solver (skeleton)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Stats:
    calls: int = 0
    assignments: int = 0
    backtracks: int = 0
    max_depth: int = 0


SolveGrid = List[List[int]]


@dataclass
class SolveResult:
    status: str
    solution: Optional[SolveGrid]
    stats: Stats
    trace: dict | None = None

