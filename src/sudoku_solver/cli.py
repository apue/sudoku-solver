"""Command-line interface entry for sudoku-solver (v1).

User-facing strings are Simplified Chinese; code uses English identifiers.
Follows the contracts in docs/design/io.md and docs/design/trace.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
import os
import time

from sudoku_solver.io.json_io import load_puzzle, load_solution_grid
from sudoku_solver.solver.backtracking import solve_backtracking
from sudoku_solver.verify.verify import verify as verify_solution
from dataclasses import asdict
from sudoku_solver.db.sqlite_writer import SQLiteResultWriter
from sudoku_solver.db.writer import build_row_from_outputs


def _db_is_enabled(args: argparse.Namespace) -> bool:
    # 默认开启；--no-db 或环境变量可关闭
    if getattr(args, "no_db", False):
        return False
    if os.getenv("SUDOKU_DB_DISABLE", "0") in ("1", "true", "True"):
        return False
    return True


def _db_path(args: argparse.Namespace) -> Path:
    p = getattr(args, "db", None) or os.getenv("SUDOKU_DB_PATH") or "var/results.sqlite3"
    return Path(p)


def _cmd_solve(args: argparse.Namespace) -> int:
    """Solve a puzzle JSON and print result JSON to stdout."""
    try:
        puzzle = load_puzzle(args.puzzle)
    except Exception as e:  # noqa: BLE001
        print(f"输入无效：{e}", file=sys.stderr)
        return 2

    t0 = time.perf_counter()
    trace_enabled = bool(getattr(args, "trace", False) or getattr(args, "trace_summary", False))
    sr, metrics = solve_backtracking(
        puzzle,
        trace_enabled=trace_enabled,
        trace_summary=bool(getattr(args, "trace_summary", False)),
    )
    # verify 成功才认为可持久化
    verify_ok = False
    if sr.solution is not None:
        try:
            verify_ok = bool(verify_solution(puzzle, sr.solution))
        except Exception:  # noqa: BLE001
            verify_ok = False
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    # 默认方法标识（仅回溯）
    method = "bt"

    result = {
        "status": sr.status,
        "solution": sr.solution,
        "stats": asdict(sr.stats),
        "trace": sr.trace if sr.trace is not None else {"enabled": False, "steps": []},
        "metrics": metrics,
    }
    out = json.dumps(result, ensure_ascii=False, indent=2)
    print(out)
    if getattr(args, "trace", False) and args.trace_file:
        Path(args.trace_file).write_text(json.dumps(result["trace"], ensure_ascii=False, indent=2))
    if getattr(args, "trace_summary", False) and args.trace_file:
        Path(args.trace_file).write_text(json.dumps(result["trace"], ensure_ascii=False, indent=2))
    # 可选：将 trace 写入文件
    if getattr(args, "trace", False) and args.trace_file:
        Path(args.trace_file).write_text(json.dumps(result["trace"], ensure_ascii=False, indent=2))
    if getattr(args, "trace_summary", False) and args.trace_file:
        Path(args.trace_file).write_text(json.dumps(result["trace"], ensure_ascii=False, indent=2))

    # DB 默认开启，verify 成功后写入
    if _db_is_enabled(args) and verify_ok:
        writer = SQLiteResultWriter(_db_path(args))
        try:
            writer.ensure_schema()
            row = build_row_from_outputs(
                test_case_id=Path(args.puzzle).name,
                method=method,
                status=sr.status,
                metrics=metrics,
                time_ms=elapsed_ms,
                created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )
            writer.write(row)
        except Exception as e:  # noqa: BLE001
            print(f"[warn] DB 持久化失败：{e}", file=sys.stderr)
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
    # DB 开关/路径
    p_solve.add_argument("--db", help="结果持久化 SQLite 路径（默认 var/results.sqlite3）")
    p_solve.add_argument("--no-db", action="store_true", help="禁用结果持久化（默认开启，verify 成功后写入）")
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
