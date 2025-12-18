"""Lightweight tracer for recording optional backtracking steps or summary."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


class Tracer:
    def __init__(self, enabled: bool = False, mode: str = "steps"):
        """Tracer supports two modes when enabled:

        - "steps": record every step into steps list
        - "summary": only keep aggregated counts
        """
        self.enabled = enabled
        self.mode = mode if enabled else "disabled"
        self.steps: List[Dict[str, Any]] = []
        self.counts: Dict[str, int] = {  # summary counters
            "choose_cell": 0,
            "assign": 0,
            "unassign": 0,
            "contradiction": 0,
            "solution_found": 0,
        }

    def _add(self, event: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        if self.mode == "steps":
            self.steps.append(event)

    @staticmethod
    def _cell_1b(r: int, c: int) -> Tuple[int, int]:
        return (r + 1, c + 1)

    def choose_cell(self, r: int, c: int, depth: int) -> None:
        self.counts["choose_cell"] += 1
        self._add({"type": "CHOOSE_CELL", "cell": self._cell_1b(r, c), "depth": depth, "reason": "first_empty"})

    def assign(self, r: int, c: int, v: int, depth: int) -> None:
        self.counts["assign"] += 1
        self._add({"type": "ASSIGN", "cell": self._cell_1b(r, c), "value": v, "depth": depth, "reason": "try_value"})

    def unassign(self, r: int, c: int, v: int, depth: int) -> None:
        self.counts["unassign"] += 1
        self._add({"type": "UNASSIGN", "cell": self._cell_1b(r, c), "value": v, "depth": depth, "reason": "backtrack"})

    def contradiction(self, r: int, c: int, depth: int, reason: str = "conflict") -> None:
        self.counts["contradiction"] += 1
        self._add({"type": "CONTRADICTION", "cell": self._cell_1b(r, c), "depth": depth, "reason": reason})

    def solution_found(self) -> None:
        self.counts["solution_found"] += 1
        self._add({"type": "SOLUTION_FOUND"})

    def to_json_obj(self) -> Dict[str, Any]:
        if not self.enabled:
            return {"enabled": False, "steps": []}
        if self.mode == "summary":
            return {"enabled": True, "mode": "summary", "counts": dict(self.counts)}
        return {"enabled": True, "mode": "steps", "steps": list(self.steps)}
