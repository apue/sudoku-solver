"""MetricsCollector: aggregates solver events into metrics per docs/metric.md."""
from __future__ import annotations

from typing import Any, Dict, Optional


class MetricsCollector:
    def __init__(self) -> None:
        self.assignments = 0
        self.backtracks = 0
        self.contradictions = 0
        self.max_depth = 0
        self.num_guess_points = 0
        self.first_guess_depth: Optional[int] = None
        self.deduced_assignments = 0
        self.guessed_assignments = 0
        self.solutions_found = 0

    # Recorder sink methods
    def decision_guess_point(self, depth: int) -> None:
        self.num_guess_points += 1
        if self.first_guess_depth is None:
            self.first_guess_depth = depth

    def decision_choose_cell(self, r: int, c: int, depth: int) -> None:  # noqa: ARG002
        # choose_cell 本身不计入 metrics；深度通过 search_update_depth 维护
        pass

    def attempt_assign(self, r: int, c: int, v: int, source: str, depth: int) -> None:  # noqa: ARG002
        self.assignments += 1
        if source == "deduced":
            self.deduced_assignments += 1
        else:
            self.guessed_assignments += 1

    def attempt_contradiction(self, r: int, c: int, v: int | None, reason: str, depth: int | None) -> None:  # noqa: ARG002
        self.contradictions += 1

    def state_unassign(self, r: int, c: int, v: int, reason: str, depth: int | None) -> None:  # noqa: ARG002
        if reason == "backtrack":
            self.backtracks += 1

    def search_update_depth(self, depth: int) -> None:
        if depth > self.max_depth:
            self.max_depth = depth

    def result_solution_found(self) -> None:
        self.solutions_found += 1

    # Public API
    def finalize(self, status: str) -> Dict[str, Any]:
        return {
            "status": status,
            "assignments": self.assignments,
            "backtracks": self.backtracks,
            "contradictions": self.contradictions,
            "max_depth": self.max_depth,
            "num_guess_points": self.num_guess_points,
            "first_guess_depth": self.first_guess_depth,
            "deduced_assignments": self.deduced_assignments,
            "guessed_assignments": self.guessed_assignments,
            "solutions_found": self.solutions_found,
        }
