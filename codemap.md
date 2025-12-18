# Code Map（v1）

本文件约束仓库结构与模块职责，避免实现发散。新增/重构模块时必须同步更新本文件。

## 目录结构（建议）

```
.
├── AGENTS.md
├── README.md
├── codemap.md
├── docs
│   ├── ROADMAP.md
│   └── design
│       ├── overview.md
│       ├── io.md
│       ├── solver_backtracking.md
│       └── trace.md
├── examples
│   ├── puzzle_easy.json
│   └── solution_easy.json
├── src
│   └── sudoku_solver
│       ├── __init__.py
│       ├── board
│       │   ├── __init__.py
│       │   └── grid.py
│       ├── io
│       │   ├── __init__.py
│       │   └── json_io.py
│       ├── trace
│       │   ├── __init__.py
│       │   └── tracer.py
│       ├── verify
│       │   ├── __init__.py
│       │   └── verify.py
│       ├── solver
│       │   ├── __init__.py
│       │   └── backtracking.py
│       ├── cli.py
│       └── types.py
└── tests
    ├── test_smoke.py
    ├── board
    ├── solver
    └── verify
```

> v1 允许暂不创建 `strategies/`；在 v1.1（候选+单元唯一）再引入。

## 模块职责

- `board/`：9×9 网格数据结构、基本合法性检查、行列宫访问工具
- `io/`：Puzzle JSON 读取与 SolveResult JSON 输出（契约见 `docs/design/io.md`）
- `solver/`：求解器实现（v1：回溯，语义见 `docs/design/solver_backtracking.md`）
- `trace/`：统计与可选步骤记录（契约见 `docs/design/trace.md`）
- `verify/`：验证器：验证解是否满足约束且不违背 givens
- `cli.py`：命令行入口与中文用户提示；将输入/输出与核心逻辑粘合
- `types.py`：公共数据类型（例如 `SolveStatus`, `SolveResult`）供各模块共享

## 依赖方向（强制）

- `cli` 可以依赖：`io`, `solver`, `verify`, `trace`, `board`, `types`
- `io` 可以依赖：`types`, `board`（用于解析/序列化）
- `solver` 可以依赖：`board`, `types`, `trace`
- `verify` 可以依赖：`board`, `types`（可选依赖 `io` 仅用于便利函数；更推荐由 `cli` 负责装载文件）
- `trace` 只能依赖：`types`（或不依赖任何业务模块）
- 任何核心模块不得依赖 `cli`

