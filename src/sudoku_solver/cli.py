"""Command-line interface entry for sudoku-solver (v1).

User-facing strings are Simplified Chinese; code uses English identifiers.
Follows the contracts in docs/design/io.md and docs/design/trace.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sudoku_solver.io.json_io import load_puzzle, load_solution_grid
from sudoku_solver.solver.backtracking import solve_backtracking
from sudoku_solver.verify.verify import verify as verify_solution
from dataclasses import asdict


def _cmd_solve(args: argparse.Namespace) -> int:
    """Solve a puzzle JSON and print result JSON to stdout."""
    try:
        puzzle = load_puzzle(args.puzzle)
    except Exception as e:  # noqa: BLE001
        print(f"输入无效：{e}", file=sys.stderr)
        return 2

    trace_enabled = bool(getattr(args, "trace", False) or getattr(args, "trace_summary", False))
    sr = solve_backtracking(
        puzzle,
        trace_enabled=trace_enabled,
        trace_summary=bool(getattr(args, "trace_summary", False)),
    )
    result = {
        "status": sr.status,
        "solution": sr.solution,
        "stats": asdict(sr.stats),
        "trace": sr.trace if sr.trace is not None else {"enabled": False, "steps": []},
    }
    out = json.dumps(result, ensure_ascii=False, indent=2)
    print(out)
    if getattr(args, "trace", False) and args.trace_file:
        Path(args.trace_file).write_text(json.dumps(result["trace"], ensure_ascii=False, indent=2))
    if getattr(args, "trace_summary", False) and args.trace_file:
        Path(args.trace_file).write_text(json.dumps(result["trace"], ensure_ascii=False, indent=2))
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    try:
        puzzle = load_puzzle(args.puzzle)
        solution = load_solution_grid(args.solution)
    except Exception as e:  # noqa: BLE001
        print(f"输入无效：{e}", file=sys.stderr)
        return 2
    ok = verify_solution(puzzle, solution)
    print(json.dumps({"ok": bool(ok)}))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sudoku-solver",
        description="数独求解器（v1：回溯，占位 CLI）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_solve = sub.add_parser("solve", help="求解一个数独 JSON 文件")
    p_solve.add_argument("puzzle", help="输入 JSON 文件路径")
    grp = p_solve.add_mutually_exclusive_group()
    grp.add_argument("--trace", action="store_true", help="开启 trace 步骤记录")
    grp.add_argument("--trace-summary", action="store_true", help="开启 trace 汇总模式（仅输出计数，不包含步骤）")
    p_solve.add_argument("--trace-file", help="将 trace 写入文件")
    p_solve.set_defaults(func=_cmd_solve)

    p_verify = sub.add_parser("verify", help="验证一个解是否满足约束")
    p_verify.add_argument("puzzle", help="输入 JSON 文件路径")
    p_verify.add_argument("--solution", required=True, help="解的 JSON 文件路径")
    p_verify.set_defaults(func=_cmd_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
