# Repository Guidelines

## Project Structure & Module Organization
- `src/sudoku_solver/` — Core package. Submodules per codemap:
  - `board/`（网格与合法性检查）
  - `solver/backtracking.py`（回溯求解，v1）
  - `verify/`（解合法性校验）
  - `io/json_io.py`（JSON I/O，契约见 `docs/design/io.md`）
  - `trace/`（stats/trace，见 `docs/design/trace.md`）
  - `cli.py`（命令行入口；中文交互）
  - `types.py`（共享类型）
- `tests/` — 与 `src/` 结构镜像（如：`tests/solver/test_backtracking.py`）。
- `examples/` — 示例输入输出（JSON）。
- 变更目录结构或职责时同步更新：`codemap.md`。

## Build, Test, and Development Commands
- Env & deps（uv）：`uv sync`（生成/更新虚拟环境与依赖）。
- Run tests：`uv run pytest -q`（或 `--maxfail=1 --disable-warnings`）。
- Lint/format：`uvx ruff check .` 与 `uvx ruff format .`。
- CLI（solve）：`uv run sudoku-solver solve examples/puzzle_easy.json [--trace] [--trace-file trace.json]`。
- CLI（verify）：`uv run sudoku-solver verify examples/puzzle_easy.json --solution examples/solution_easy.json`。
- CI 要求：ruff 无报错 + pytest 全绿。

## Coding Style & Naming Conventions
- Python：4 空格缩进，PEP 8；公共 API 必须加类型标注。
- 命名：模块/函数/变量 `snake_case`；类 `CamelCase`；常量 `UPPER_SNAKE_CASE`。
- 依赖方向（强约束，见 `codemap.md`）：核心模块不得依赖 `cli`；`trace` 仅依赖 `types`。
- 逻辑与 I/O/CLI 分离；核心算法不做打印。

## Testing Guidelines
- 框架：`pytest`；测试路径镜像源码路径。
- 命名：`tests/**/test_*.py`；函数 `test_*`，清晰 Arrange/Act/Assert。
- 覆盖重点：`solver/backtracking`、`verify`、`io`；覆盖边界：无解、多解、极少 givens、非法输入。
- 可选：`hypothesis` 做不变量/随机盘面校验。

## Commit & Pull Request Guidelines
- Conventional Commits：`feat: fix: refactor: test: docs: chore:`。
- 小步提交；非显而易见的变更在提交体内写清“原因/口径”。
- PR 必需：变更摘要、关联 issue、I/O/CLI 影响说明、测试覆盖。
- 合并前 CI 必须为绿；不得引入 `ruff` 报错或忽略关键测试。

## Language & Interaction
- 全局：所有用户交互使用简体中文（CLI 帮助、错误、日志、README 示例）。
- 代码保持英文（标识符、注释、docstrings）。
- 可在用户输出中使用中英夹注以提高清晰度。
- 例：`print("请输入数独谜题文件路径：")  # Request input file path`

## I/O & CLI Contract
- I/O 契约：严格遵循 `docs/design/io.md` 与 `docs/design/trace.md`。
- 状态语义：`unique | multiple | unsat`；`unsat` 时 `solution=null`。
- `--trace` 默认关闭；开启后输出 `trace.enabled=true` 与 `steps`；`--trace-file` 可额外写文件。

## Security & Configuration Tips
- 离线运行：不依赖网络；示例数据存放在 `examples/`。
- 可复现：避免隐藏全局；必要时显式传入随机种子。
- 大文件不入库；使用 `.gitignore` 忽略生成物。
