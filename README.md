# sudoku-solver

一个**离线运行**的标准 9×9 数独求解器（v1：纯回溯），支持：

- **唯一解**（`status=unique`）
- **多解**（`status=multiple`，会返回其中任意一个解）
- **无解**（`status=unsat`）

并提供两类输出：

- **stats**：始终输出的统计信息（回溯次数等）
- **metrics**：事件驱动聚合指标，字段见 `docs/metric.md`
- **trace**：默认关闭，`--trace`/`--trace-summary` 打开（教学/汇总）

## 安装与运行（uv）

```bash
uv sync
```

若遇到构建错误（例如提示 `src` 不存在），先执行：

```bash
make bootstrap && make sync
```

### 求解

```bash
# 求解（默认：只输出 stats，不输出 trace steps）
uv run sudoku-solver solve examples/puzzle_easy.json

# 开启 trace（输出到 stdout）
uv run sudoku-solver solve examples/puzzle_easy.json --trace

# 开启 trace 并写入文件（同时 stdout 仍输出结果 JSON）
uv run sudoku-solver solve examples/puzzle_easy.json --trace --trace-file trace.json

# 结果持久化（SQLite，默认开启，verify 成功后落库）
uv run sudoku-solver solve examples/puzzle_easy.json --db var/results.sqlite3   # 自定义路径
uv run sudoku-solver solve examples/puzzle_easy.json --no-db                    # 禁用持久化
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
- Metrics：`docs/metric.md` 与 `docs/design/metrics-collector-design.md`
- DB Schema：`docs/design/db-design.md`
- 目录与依赖约束：`codemap.md`
- 路线图：`docs/ROADMAP.md`

## 结果数据库与版本控制

- 本地 SQLite 默认路径：`var/results.sqlite3`（已在 `.gitignore` 中忽略）。
- 建议将数据作为导出快照提交：`make db.export` 生成 CSV。
