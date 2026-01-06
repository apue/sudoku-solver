# Code Map（v2）

本文件约束仓库结构与模块职责，避免实现发散。新增/重构模块时必须同步更新本文件。

## 目录结构（建议）

```
.
├── .jupyter
│   └── jupyter_server_config.py
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
│       ├── strategies
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── candidates.py
│       │   ├── policies.py
│       │   ├── naked_single.py
│       │   ├── hidden_single.py
│       │   ├── naked_pair.py
│       │   ├── pointing.py
│       │   └── claiming.py
│       ├── solver
│       │   ├── __init__.py
│       │   └── backtracking.py
│       ├── metrics
│       │   └── collector.py
│       ├── instrumentation
│       │   └── recorder.py
│       ├── db
│       │   ├── __init__.py
│       │   ├── writer.py
│       │   └── sqlite_writer.py
│       ├── cli.py
│       ├── notebook
│       │   ├── __init__.py
│       │   └── visualizer.py
│       └── types.py
├── notebooks
│   ├── README.md
│   └── policy_explorer.ipynb
├── scripts
│   └── policy_benchmark.py
├── benchmarks
│   └── README.md
└── tests
    ├── test_smoke.py
    ├── board
    ├── solver
    └── verify
```

> v2 起 `strategies/`、`metrics/`、`instrumentation/` 为核心模块，`scripts/` 与 `benchmarks/` 提供对比工具。

## 模块职责

- `board/`：9×9 网格数据结构、基本合法性检查、行列宫访问工具
- `io/`：Puzzle JSON 读取与 SolveResult JSON 输出（契约见 `docs/design/io.md`）
- `solver/`：求解器实现（v1：回溯，语义见 `docs/design/solver_backtracking.md`）
- `trace/`：统计与可选步骤记录（契约见 `docs/design/trace.md`）
- `strategies/`：规则库 + policy runner，提供 `StrategyStep` schema
- `metrics/`：聚合 Recorder 事件输出指标
- `instrumentation/`：Recorder（事件总线），供 metrics/trace 共用
- `db/`：结果持久化（SQLite）
- `notebook/`：Notebook/ipywidgets 可视化 helper（不依赖 CLI）
- `verify/`：验证器：验证解是否满足约束且不违背 givens
- `cli.py`：命令行入口与中文用户提示；将输入/输出与核心逻辑粘合
- `types.py`：公共数据类型（例如 `SolveStatus`, `SolveResult`）供各模块共享
- `scripts/`：辅助脚本（policy benchmark）
- `benchmarks/`：基准题库 / 说明
- `.jupyter/`：项目内 Jupyter 配置（保存时自动清理输出）

## 依赖方向（强制）

- `cli` 可以依赖：`io`, `solver`, `verify`, `trace`, `board`, `types`
- `io` 可以依赖：`types`, `board`（用于解析/序列化）
- `solver` 可以依赖：`board`, `types`, `trace`, `strategies`, `metrics`, `instrumentation`
- `verify` 可以依赖：`board`, `types`（可选依赖 `io` 仅用于便利函数；更推荐由 `cli` 负责装载文件）
- `trace` 只能依赖：`types`、`instrumentation`（只消费事件）
- `strategies` 不可依赖 `cli/io/trace`; 仅依赖 `board`, `types`
- `metrics` 仅依赖 `types`
- `instrumentation` 不依赖业务模块
- `notebook` 可以依赖：`io`, `solver`, `strategies`, `trace`, `board`, `types`
- 任何核心模块不得依赖 `cli`
