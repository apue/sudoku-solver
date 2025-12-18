"""Result persistence interfaces.

Defines a minimal writer abstraction so we can swap storage backends
without touching solver or CLI logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable, Optional, Dict, Any


@dataclass
class PersistRow:
    """Canonical row to persist into the results store.

    Matches docs/design/db-design.md (field names align with SQLite schema).
    """

    test_case_id: str
    method: str

    status: str
    solutions_found: int

    assignments: int
    backtracks: int
    contradictions: int
    max_depth: int

    num_guess_points: int
    first_guess_depth: Optional[int]
    deduced_assignments: int
    guessed_assignments: int

    time_ms: Optional[int]
    created_at: str  # ISO-8601


@runtime_checkable
class ResultWriter(Protocol):
    def ensure_schema(self) -> None:  # pragma: no cover - thin wrapper
        """Create tables if needed (idempotent)."""

    def write(self, row: PersistRow) -> None:  # pragma: no cover - thin wrapper
        """Persist one row."""


def build_row_from_outputs(
    *,
    test_case_id: str,
    method: str,
    status: str,
    metrics: Dict[str, Any],
    time_ms: Optional[int],
    created_at: str,
) -> PersistRow:
    """Map solver outputs + metrics to PersistRow with strict fields."""
    return PersistRow(
        test_case_id=test_case_id,
        method=method,
        status=status,
        solutions_found=int(metrics.get("solutions_found", 0)),
        assignments=int(metrics.get("assignments", 0)),
        backtracks=int(metrics.get("backtracks", 0)),
        contradictions=int(metrics.get("contradictions", 0)),
        max_depth=int(metrics.get("max_depth", 0)),
        num_guess_points=int(metrics.get("num_guess_points", 0)),
        first_guess_depth=metrics.get("first_guess_depth"),
        deduced_assignments=int(metrics.get("deduced_assignments", 0)),
        guessed_assignments=int(metrics.get("guessed_assignments", 0)),
        time_ms=time_ms if time_ms is not None else None,
        created_at=created_at,
    )

