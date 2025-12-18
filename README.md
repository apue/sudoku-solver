# sudoku-solver

一个**离线运行**的标准 9×9 数独求解器（v1：纯回溯），支持：

- **唯一解**（`status=unique`）
- **多解**（`status=multiple`，会返回其中任意一个解）
- **无解**（`status=unsat`）

并提供两类输出：

- **stats**：始终输出的统计信息（回溯次数等）
- **trace**：默认关闭，使用 `--trace` 打开（用于后续“教学模式/解释输出”）

## 安装与运行（uv）

```bash
uv sync
```

### 求解

```bash
# 求解（默认：只输出 stats，不输出 trace steps）
uv run sudoku-solver solve examples/puzzle_easy.json

# 开启 trace（输出到 stdout）
uv run sudoku-solver solve examples/puzzle_easy.json --trace

# 开启 trace 并写入文件（同时 stdout 仍输出结果 JSON）
uv run sudoku-solver solve examples/puzzle_easy.json --trace --trace-file trace.json
```

### 验证

```bash
# 验证一个“解”是否满足标准数独约束且不违背 givens
uv run sudoku-solver verify examples/puzzle_easy.json --solution examples/solution_easy.json
```

## 输入输出约定（v1）

- 输入：JSON 文件，形如：

```json
{
  "grid": [
    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],

    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],

    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0]
  ]
}
```

- 输出：JSON（`status` + `solution?` + `stats` + `trace?`）

更详细的契约与字段说明见：

- `docs/design/io.md`
- `docs/design/trace.md`
- `docs/design/solver_backtracking.md`

## 文档入口

- 架构总览：`docs/design/overview.md`
- I/O 契约：`docs/design/io.md`
- 回溯语义：`docs/design/solver_backtracking.md`
- Trace/Stats：`docs/design/trace.md`
- 目录与依赖约束：`codemap.md`
- 路线图：`docs/ROADMAP.md`
