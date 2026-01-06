# Trace / Stats（v2）

本文件定义 v1 的统计（Stats）与可选 trace summary 契约。

设计目标：

- **stats 永远开**：即使 `--trace` 未开启，也应输出统计指标（至少包含 v1 最小集合）
- **trace summary 可选**：仅在 `--trace` 开启时输出汇总计数，为后续“教学模式/可解释性”扩展保留铺垫
- Trace summary 记录应轻量且易持久化，同时为 v3（可解释）保留 `strategy_steps` 接口

## Stats（必选）

建议字段（v1 最小集合用 ✅ 标出）：

- ✅ `calls`：递归调用次数 / 节点访问次数
- ✅ `assignments`：赋值尝试次数
- ✅ `backtracks`：回退次数
- ✅ `max_depth`：最大搜索深度
- （可选）`solutions_found`：找到的解个数（0/1/2）
- （可选）`elapsed_ms`：耗时（若实现容易）

> 注意：字段含义以 `docs/design/solver_backtracking.md` 为准；如口径调整，需同步修改两处文档。

## Trace（可选）

v2 仍默认输出 summary，但新增 `strategy_counts`，并允许 `mode=steps` 时输出结构化步骤：

```json
{
  "enabled": true,
  "mode": "summary",
  "counts": { ... },
  "strategy_counts": {
    "naked_single": 12,
    "hidden_single": 3,
    "pointing": 2
  }
}
```

### 字段约定

- `enabled`：是否开启 trace（由 CLI 参数决定）
- `mode`：`summary`（默认）或 `steps`
- `counts`：事件类型 -> 次数（详见 `Tracer` 实现）
- `strategy_counts`：策略名 -> 命中次数，供 v2/v3 对比
- `strategy_steps`：仅在 `mode=steps` 时输出（见下）

## Strategy Step Schema（v2）

`--trace --trace-mode steps` 时，在 summary 字段基础上追加 `strategy_steps`：

```json
{
  "strategy": "pointing",
  "depth": 3,
  "description": "r1c1, r1c2 限制 5 只能沿行延伸",
  "assignments": [
    {"cell": [1, 3], "value": 4, "reason": "unit_unique"}
  ],
  "eliminations": [
    {"cell": [1, 5], "values": [5], "reason": "pointing_row"}
  ],
  "metadata": {"value": 5}
}
```

该 schema 即 v3 Notebook/Web 渲染所消费的接口：

- `assignments`：包含 cell（1-based）、value、reason/note
- `eliminations`：包含 cell（1-based）、values（升序数组）、reason/note
- `metadata`：策略可选字段（如 `value`, `unit`）供 UI 展示

> Summary 模式不输出 `strategy_steps`，仅保留 `strategy_counts` 以避免终端噪声。

## CLI 行为要求（与 trace 相关）

- 默认：`--trace` 关闭，仅输出 `stats`（以及 `status/solution`）
- `--trace`：开启 summary，并在结果 JSON 中输出 `trace.enabled=true`、`mode=summary`
- `--trace-file <path>`：将 summary 写入文件；若未指定，则写入 `var/traces/<puzzle>.<timestamp>.trace.json`
  - 目录 `var/` 已在仓库 `.gitignore` 中忽略，可安全存放运行产物

具体参数名与帮助文本以 README 为准。
