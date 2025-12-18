"""SQLite implementation of ResultWriter.

Uses Python stdlib sqlite3 to avoid extra dependencies.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from .writer import PersistRow, ResultWriter


class SQLiteResultWriter(ResultWriter):
    def __init__(self, db_path: str | Path) -> None:
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.path))

    def ensure_schema(self) -> None:
        sql = (
            "CREATE TABLE IF NOT EXISTS results (\n"
            "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
            "    test_case_id TEXT NOT NULL,\n"
            "    method TEXT NOT NULL,\n"
            "    status TEXT NOT NULL,\n"
            "    solutions_found INTEGER NOT NULL,\n"
            "    assignments INTEGER NOT NULL,\n"
            "    backtracks INTEGER NOT NULL,\n"
            "    contradictions INTEGER NOT NULL,\n"
            "    max_depth INTEGER NOT NULL,\n"
            "    num_guess_points INTEGER NOT NULL,\n"
            "    first_guess_depth INTEGER,\n"
            "    deduced_assignments INTEGER NOT NULL,\n"
            "    guessed_assignments INTEGER NOT NULL,\n"
            "    time_ms INTEGER,\n"
            "    created_at TEXT NOT NULL\n"
            ");"
        )
        with self._connect() as con:
            con.execute(sql)

    def write(self, row: PersistRow) -> None:
        with self._connect() as con:
            con.execute(
                (
                    "INSERT INTO results (test_case_id, method, status, solutions_found, "
                    "assignments, backtracks, contradictions, max_depth, num_guess_points, "
                    "first_guess_depth, deduced_assignments, guessed_assignments, time_ms, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                ),
                (
                    row.test_case_id,
                    row.method,
                    row.status,
                    row.solutions_found,
                    row.assignments,
                    row.backtracks,
                    row.contradictions,
                    row.max_depth,
                    row.num_guess_points,
                    row.first_guess_depth,
                    row.deduced_assignments,
                    row.guessed_assignments,
                    row.time_ms,
                    row.created_at,
                ),
            )

