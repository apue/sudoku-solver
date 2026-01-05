from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def positive_puzzle_path(project_root: Path) -> Path:
    return project_root / "data" / "001.json"


@pytest.fixture(scope="session")
def conflict_puzzle_path(project_root: Path) -> Path:
    return project_root / "tests" / "data" / "puzzle_conflict.json"


@pytest.fixture(scope="session")
def example_puzzle_path(project_root: Path) -> Path:
    return project_root / "examples" / "puzzle_easy.json"


@pytest.fixture(scope="session")
def example_solution_path(project_root: Path) -> Path:
    return project_root / "examples" / "solution_easy.json"


@pytest.fixture()
def disable_db(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUDOKU_DB_DISABLE", "1")


@pytest.fixture()
def trace_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "trace-artifacts"
    monkeypatch.setenv("SUDOKU_TRACE_DIR", str(path))
    return path
