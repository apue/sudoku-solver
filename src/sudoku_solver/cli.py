"""Command-line interface entry for sudoku-solver (v1 placeholder).

User-facing strings are Simplified Chinese; code uses English identifiers.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _cmd_solve(args: argparse.Namespace) -> int:
    """Placeholder solve command matching README contract.

    Prints a simple JSON stub to stdout to validate the CLI wiring.
    """
    puzzle_path = Path(args.puzzle)
    if not puzzle_path.exists():
        print(f"找不到输入文件：{puzzle_path}", file=sys.stderr)
        return 2
    # Minimal echo to confirm flow; not an actual solver.
    result = {
        "status": "unsat",
        "solution": None,
        "stats": {"calls": 0, "assignments": 0, "backtracks": 0, "max_depth": 0},
        "trace": {"enabled": bool(args.trace), "steps": []},
    }
    print(json.dumps(result, ensure_ascii=False))
    if args.trace and args.trace_file:
        Path(args.trace_file).write_text(json.dumps(result["trace"], ensure_ascii=False))
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    """Placeholder verify command: only checks files exist."""
    puzzle_path = Path(args.puzzle)
    solution_path = Path(args.solution)
    missing = [p for p in (puzzle_path, solution_path) if not Path(p).exists()]
    if missing:
        print("找不到文件：" + ", ".join(map(str, missing)), file=sys.stderr)
        return 2
    print("{\"ok\": true, \"reason\": \"placeholder\"}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sudoku-solver",
        description="数独求解器（v1：回溯，占位 CLI）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_solve = sub.add_parser("solve", help="求解一个数独 JSON 文件")
    p_solve.add_argument("puzzle", help="输入 JSON 文件路径")
    p_solve.add_argument("--trace", action="store_true", help="开启 trace 记录")
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

