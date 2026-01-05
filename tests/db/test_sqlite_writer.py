from __future__ import annotations

import sqlite3
from pathlib import Path

from sudoku_solver.db.sqlite_writer import SQLiteResultWriter
from sudoku_solver.db.writer import build_row_from_outputs


METRICS_SAMPLE = {
    "status": "unique",
    "assignments": 10,
    "backtracks": 2,
    "contradictions": 3,
    "max_depth": 4,
    "num_guess_points": 1,
    "first_guess_depth": 2,
    "deduced_assignments": 0,
    "guessed_assignments": 10,
    "solutions_found": 1,
}


def test_build_row_from_outputs_maps_fields() -> None:
    row = build_row_from_outputs(
        test_case_id="case.json",
        method="bt",
        status="unique",
        metrics=METRICS_SAMPLE,
        time_ms=5,
        created_at="2024-01-01T00:00:00Z",
    )
    assert row.assignments == METRICS_SAMPLE["assignments"]
    assert row.first_guess_depth == METRICS_SAMPLE["first_guess_depth"]
    assert row.method == "bt"


def test_sqlite_writer_persists_row(tmp_path: Path) -> None:
    db_path = tmp_path / "results.sqlite3"
    writer = SQLiteResultWriter(db_path)
    writer.ensure_schema()
    row = build_row_from_outputs(
        test_case_id="case.json",
        method="bt",
        status="unique",
        metrics=METRICS_SAMPLE,
        time_ms=10,
        created_at="2024-01-01T00:00:00Z",
    )
    writer.write(row)

    with sqlite3.connect(db_path) as con:
        cur = con.execute(
            "SELECT test_case_id, method, status, assignments, solutions_found FROM results"
        )
        stored = cur.fetchone()
        assert stored == ("case.json", "bt", "unique", METRICS_SAMPLE["assignments"], 1)
