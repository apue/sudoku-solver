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
    trace_data = json.loads(trace_file.read_text())
    assert trace_data["enabled"] is True
    assert trace_data["mode"] == "summary"
    assert "strategy_counts" in trace_data


def test_cli_can_disable_deductions(positive_puzzle_path: Path, disable_db: None, capsys) -> None:  # noqa: ANN001
    exit_code = cli.main([
        "solve",
        str(positive_puzzle_path),
        "--no-deductions",
    ])
    captured = capsys.readouterr()
    assert exit_code == 0
    result = json.loads(captured.out)
    assert result["metrics"]["deduced_assignments"] == 0


def test_cli_solve_without_trace_file_uses_env_dir(
    positive_puzzle_path: Path,
    disable_db: None,  # noqa: ANN001
    trace_dir: Path,
    capsys,
) -> None:
    exit_code = cli.main([
        "solve",
        str(positive_puzzle_path),
        "--trace",
    ])
    captured = capsys.readouterr()
    assert exit_code == 0
    result = json.loads(captured.out)
    assert result["trace"]["mode"] == "summary"
    artifacts = list(trace_dir.glob("*.trace.json"))
    assert len(artifacts) == 1
    trace_data = json.loads(artifacts[0].read_text())
    assert trace_data["mode"] == "summary"


def test_cli_solve_with_invalid_input_returns_error(conflict_puzzle_path: Path, disable_db: None, capsys) -> None:  # noqa: ANN001
    exit_code = cli.main(["solve", str(conflict_puzzle_path)])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "输入无效" in captured.err


def test_cli_solve_with_policy_and_compare(
    positive_puzzle_path: Path,
    disable_db: None,  # noqa: ANN001
    capsys,
) -> None:
    exit_code = cli.main([
        "solve",
        str(positive_puzzle_path),
        "--policy",
        "human-lite",
        "--compare-policy",
        "default",
    ])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert "primary" in payload and "comparison" in payload
    assert payload["primary"]["policy"] == "human-lite"


def test_cli_solve_with_invalid_policy_reports_error(
    positive_puzzle_path: Path,
    disable_db: None,  # noqa: ANN001
    capsys,
) -> None:
    exit_code = cli.main([
        "solve",
        str(positive_puzzle_path),
        "--policy",
        "unknown-policy",
    ])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "策略配置错误" in captured.err


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
