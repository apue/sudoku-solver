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
        self.strategy_counts: Dict[str, int] = {}
        self.strategy_steps: List[Dict[str, Any]] = []

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

    def strategy_step(
        self,
        *,
        strategy: str,
        depth: int,
        description: str,
        assignments: List[Dict[str, Any]],
        eliminations: List[Dict[str, Any]],
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        if not self.enabled:
            return
        self.strategy_counts[strategy] = self.strategy_counts.get(strategy, 0) + 1
        if self.mode != "steps":
            return
        payload = {
            "strategy": strategy,
            "depth": depth,
            "description": description,
            "assignments": assignments,
            "eliminations": eliminations,
            "metadata": metadata or {},
        }
        self.strategy_steps.append(payload)

    def to_json_obj(self) -> Dict[str, Any]:
        if not self.enabled:
            return {"enabled": False, "steps": []}
        if self.mode == "summary":
            return {
                "enabled": True,
                "mode": "summary",
                "counts": dict(self.counts),
                "strategy_counts": dict(self.strategy_counts),
            }
        return {
            "enabled": True,
            "mode": "steps",
            "steps": list(self.steps),
            "strategy_counts": dict(self.strategy_counts),
            "strategy_steps": list(self.strategy_steps),
        }


class TraceSink:
    """Adapter sink that maps Recorder events to a Tracer instance."""

    def __init__(self, tracer: Tracer) -> None:
        self._t = tracer

    # decision
    def decision_choose_cell(self, r: int, c: int, depth: int) -> None:
        self._t.choose_cell(r, c, depth)

    def decision_guess_point(self, depth: int) -> None:  # noqa: ARG002
        # Not a dedicated tracer event; represented implicitly by choose_cell
        pass

    # attempt
    def attempt_assign(self, r: int, c: int, v: int, source: str, depth: int) -> None:  # noqa: ARG002
        self._t.assign(r, c, v, depth=depth)

    def attempt_contradiction(self, r: int, c: int, v: int | None, reason: str, depth: int | None) -> None:  # noqa: ARG002
        self._t.contradiction(r, c, depth=depth or 0, reason=reason)

    # state
    def state_unassign(self, r: int, c: int, v: int, reason: str, depth: int | None) -> None:  # noqa: ARG002
        self._t.unassign(r, c, v, depth=depth or 0)

    # search
    def search_update_depth(self, depth: int) -> None:  # noqa: ARG002
        pass

    # result
    def result_solution_found(self) -> None:
        self._t.solution_found()

    def strategy_step(self, step: Any, depth: int) -> None:
        assignments = [
            {
                "cell": self._t._cell_1b(action.row, action.col),
                "value": action.value,
                "reason": action.reason,
                "note": action.note,
            }
            for action in getattr(step, "assignments", [])
        ]
        eliminations = [
            {
                "cell": self._t._cell_1b(action.row, action.col),
                "values": sorted(action.values),
                "reason": action.reason,
                "note": action.note,
            }
            for action in getattr(step, "eliminations", [])
        ]
        self._t.strategy_step(
            strategy=getattr(step, "strategy", "unknown"),
            depth=depth,
            description=getattr(step, "description", ""),
            assignments=assignments,
            eliminations=eliminations,
            metadata=getattr(step, "metadata", {}) or {},
        )
