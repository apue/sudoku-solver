# sudoku-solver

一个**离线运行**的标准 9×9 数独求解器（v2：回溯 + 策略 policy：裸显单/隐显单 + 裸对/pointing/claiming），支持：

- **唯一解**（`status=unique`）
- **多解**（`status=multiple`，会返回其中任意一个解）
- **无解**（`status=unsat`）

并提供两类输出：

- **stats**：始终输出的统计信息（回溯次数等）
- **metrics**：事件驱动聚合指标，字段见 `docs/metric.md`
- **trace**：默认关闭，`--trace` 打开 summary；`--trace-mode steps` 可导出策略步骤（为 v3 可解释留口）
- **候选推理**：policy 可配置（`--policy default` / `human-lite` 等）；`--strategies a,b` 可自定义顺序；`--no-deductions` 可退回纯回溯
- **策略对比**：`--compare-policy other` 同时运行两套策略输出对比；`scripts/policy_benchmark.py` 可批量跑基准

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
# 求解（默认：policy=default，trace summary 关闭）
uv run sudoku-solver solve examples/puzzle_easy.json

# 开启 trace summary（stdout 附带 summary JSON，trace 文件默认写入 var/traces/...）
uv run sudoku-solver solve examples/puzzle_easy.json --trace

# 输出策略步骤（trace steps mode，仅在 --trace 同时开启时输出策略步骤 JSON）
uv run sudoku-solver solve examples/puzzle_easy.json --trace --trace-mode steps

# 自定义 trace 文件路径（若不指定则写入 var/traces/<puzzle>.<ts>.trace.json）
uv run sudoku-solver solve examples/puzzle_easy.json --trace --trace-file trace.json

# 切换 policy / 自定义策略顺序
uv run sudoku-solver solve data/002.json --policy human-lite
uv run sudoku-solver solve data/002.json --strategies naked_single,hidden_single,naked_pair

# 同一 puzzle 对比两套 policy（stdout 输出 primary/comparison）
uv run sudoku-solver solve data/002.json --policy human-lite --compare-policy default

# 禁用候选推理，退回纯回溯
uv run sudoku-solver solve examples/puzzle_easy.json --no-deductions

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
- 可解释接口：`docs/design/explainability.md`

## 结果数据库与版本控制

- 本地 SQLite 默认路径：`var/results.sqlite3`（已在 `.gitignore` 中忽略）。
- 建议将数据作为导出快照提交：`make db.export` 生成 CSV。
- Trace 文件默认写入 `var/traces/`，可用 `SUDOKU_TRACE_DIR` 自定义；该目录同样已忽略。

## Policy Benchmark

- 单次对比：使用 `--compare-policy`。
- 批量基准：`python scripts/policy_benchmark.py --puzzles data/001.json data/002.json --policies human-lite default`。
- 结果 CSV 默认存于 `var/benchmarks/benchmark.<ts>.csv`，字段包含 `status/time_ms/assignments/backtracks/...`。
