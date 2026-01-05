"""Command-line interface entry for sudoku-solver (v1).

User-facing strings are Simplified Chinese; code uses English identifiers.
Follows the contracts in docs/design/io.md and docs/design/trace.md.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from uuid import uuid4

from dataclasses import asdict

from sudoku_solver.db.sqlite_writer import SQLiteResultWriter
from sudoku_solver.db.writer import build_row_from_outputs
from sudoku_solver.io.json_io import load_puzzle, load_solution_grid
from sudoku_solver.solver.backtracking import solve_backtracking
from sudoku_solver.verify.verify import verify as verify_solution

TRACE_DIR_ENV = "SUDOKU_TRACE_DIR"
DEFAULT_TRACE_DIR = Path("var/traces")


def _deductions_enabled(args: argparse.Namespace) -> bool:
    return not getattr(args, "no_deductions", False)


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


def _trace_requested(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "trace", False))


def _default_trace_target(args: argparse.Namespace) -> Path:
    base = Path(os.getenv(TRACE_DIR_ENV, str(DEFAULT_TRACE_DIR)))
    base.mkdir(parents=True, exist_ok=True)
    puzzle_name = Path(args.puzzle).stem or "puzzle"
    stamp = time.strftime("%Y%m%dT%H%M%S")
    suffix = uuid4().hex[:6]
    return base / f"{puzzle_name}.{stamp}.{suffix}.trace.json"


def _write_trace_file(args: argparse.Namespace, trace_obj: dict | None) -> None:
    if not _trace_requested(args) or trace_obj is None:
        return
    trace_file = getattr(args, "trace_file", None)
    target = Path(trace_file) if trace_file else _default_trace_target(args)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(trace_obj, ensure_ascii=False, indent=2))


def _cmd_solve(args: argparse.Namespace) -> int:
    """Solve a puzzle JSON and print result JSON to stdout."""
    try:
        puzzle = load_puzzle(args.puzzle)
    except Exception as e:  # noqa: BLE001
        print(f"输入无效：{e}", file=sys.stderr)
        return 2

    t0 = time.perf_counter()
    trace_enabled = _trace_requested(args)
    sr, metrics = solve_backtracking(
        puzzle,
        trace_enabled=trace_enabled,
        trace_mode="summary",
        use_deductions=_deductions_enabled(args),
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

    trace_obj = sr.trace if sr.trace is not None else {"enabled": False, "mode": "summary", "counts": {}}
    result = {
        "status": sr.status,
        "solution": sr.solution,
        "stats": asdict(sr.stats),
        "trace": trace_obj,
        "metrics": metrics,
    }
    out = json.dumps(result, ensure_ascii=False, indent=2)
    print(out)
    _write_trace_file(args, trace_obj)

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
    p_solve.add_argument("--trace", action="store_true", help="开启 trace summary（mode=summary）")
    p_solve.add_argument("--trace-file", help="将 trace summary 写入文件（默认写入 var/traces/）")
    p_solve.add_argument(
        "--no-deductions",
        action="store_true",
        help="禁用候选推理（默认启用 naked/hidden single 推进）",
    )
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
