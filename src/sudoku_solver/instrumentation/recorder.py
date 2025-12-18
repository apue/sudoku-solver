"""Event Recorder and sink interface for metrics/trace decoupling.

Solver/strategies emit normalized events into `Recorder`, which forwards
to registered sinks (e.g., MetricsCollector, TraceSink). Sinks may
implement any subset of event handlers via duck-typing.
"""
from __future__ import annotations

from typing import Any, List


class Recorder:
    def __init__(self, sinks: List[Any] | None = None) -> None:
        self._sinks = list(sinks or [])
        # Provide grouped facades for ergonomics
        self.decision = _Decision(self)
        self.attempt = _Attempt(self)
        self.state = _State(self)
        self.search = _Search(self)
        self.result = _Result(self)

    def _call(self, name: str, *args: Any, **kwargs: Any) -> None:
        for s in self._sinks:
            fn = getattr(s, name, None)
            if fn:
                fn(*args, **kwargs)


class _Decision:
    def __init__(self, rec: Recorder) -> None:
        self._rec = rec

    def choose_cell(self, r: int, c: int, depth: int) -> None:
        self._rec._call("decision_choose_cell", r, c, depth)

    def guess_point(self, depth: int) -> None:
        self._rec._call("decision_guess_point", depth)


class _Attempt:
    def __init__(self, rec: Recorder) -> None:
        self._rec = rec

    def assign(self, r: int, c: int, v: int, source: str, depth: int) -> None:
        self._rec._call("attempt_assign", r, c, v, source, depth)

    def contradiction(self, r: int, c: int, v: int | None = None, reason: str = "invalid_candidate", depth: int | None = None) -> None:
        self._rec._call("attempt_contradiction", r, c, v, reason, depth)


class _State:
    def __init__(self, rec: Recorder) -> None:
        self._rec = rec

    def unassign(self, r: int, c: int, v: int, reason: str = "backtrack", depth: int | None = None) -> None:
        self._rec._call("state_unassign", r, c, v, reason, depth)


class _Search:
    def __init__(self, rec: Recorder) -> None:
        self._rec = rec

    def update_depth(self, depth: int) -> None:
        self._rec._call("search_update_depth", depth)


class _Result:
    def __init__(self, rec: Recorder) -> None:
        self._rec = rec

    def solution_found(self) -> None:
        self._rec._call("result_solution_found")
