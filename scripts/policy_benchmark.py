#!/usr/bin/env python3
"""Policy benchmark helper.

Run multiple solver policies against a set of puzzles and emit CSV summary.
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path
from typing import Iterable, List

from sudoku_solver.io.json_io import load_puzzle
from sudoku_solver.solver.backtracking import solve_backtracking


def _run_case(puzzle_path: Path, policy: str) -> dict:
    grid = load_puzzle(puzzle_path)
    t0 = time.perf_counter()
    result, metrics = solve_backtracking(grid, trace_enabled=False, use_deductions=True, strategy_policy=policy)
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    return {
        "puzzle": puzzle_path.name,
        "policy": policy,
        "status": result.status,
        "time_ms": elapsed_ms,
        "assignments": result.stats.assignments,
        "backtracks": result.stats.backtracks,
        "deduced_assignments": metrics.get("deduced_assignments"),
        "num_guess_points": metrics.get("num_guess_points"),
    }


def _resolve_puzzles(patterns: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for p in patterns:
        path = Path(p)
        if path.is_file():
            files.append(path)
        else:
            files.extend(sorted(Path(".").glob(p)))
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Policy benchmark runner")
    parser.add_argument("--puzzles", nargs="+", default=["data/*.json"], help="Puzzle 文件或 glob")
    parser.add_argument("--policies", nargs="+", default=["human-lite", "default"], help="policy 列表")
    parser.add_argument("--output", help="输出 CSV 路径（默认 var/benchmarks/<ts>.csv）")
    args = parser.parse_args(argv)

    puzzles = _resolve_puzzles(args.puzzles)
    if not puzzles:
        raise SystemExit("未找到 puzzle 文件")

    if args.output:
        output_path = Path(args.output)
    else:
        stamp = time.strftime("%Y%m%dT%H%M%S")
        output_path = Path("var/benchmarks") / f"benchmark.{stamp}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows: List[dict] = []
    for puzzle in puzzles:
        for policy in args.policies:
            row = _run_case(puzzle, policy)
            rows.append(row)
            print(f"{puzzle.name} @ {policy}: {row['status']} ({row['time_ms']} ms)")

    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "puzzle",
                "policy",
                "status",
                "time_ms",
                "assignments",
                "backtracks",
                "deduced_assignments",
                "num_guess_points",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"结果写入 {output_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
