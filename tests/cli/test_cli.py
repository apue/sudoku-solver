from __future__ import annotations

import json
from pathlib import Path

from sudoku_solver import cli


def test_cli_solve_outputs_json(positive_puzzle_path: Path, tmp_path: Path, disable_db: None, capsys) -> None:  # noqa: ANN001
    trace_file = tmp_path / "trace.json"
    exit_code = cli.main([
        "solve",
        str(positive_puzzle_path),
        "--trace",
        "--trace-file",
        str(trace_file),
    ])
    captured = capsys.readouterr()
    assert exit_code == 0
    result = json.loads(captured.out)
    assert result["status"] in {"unique", "multiple"}
    assert json.loads(trace_file.read_text())["enabled"] is True


def test_cli_solve_with_invalid_input_returns_error(conflict_puzzle_path: Path, disable_db: None, capsys) -> None:  # noqa: ANN001
    exit_code = cli.main(["solve", str(conflict_puzzle_path)])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "输入无效" in captured.err


def test_cli_verify_reports_ok(example_puzzle_path: Path, example_solution_path: Path, capsys) -> None:  # noqa: ANN001
    exit_code = cli.main([
        "verify",
        str(example_puzzle_path),
        "--solution",
        str(example_solution_path),
    ])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload == {"ok": True}
