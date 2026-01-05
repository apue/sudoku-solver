# Trace / Stats（v1）

本文件定义 v1 的统计（Stats）与可选 trace summary 契约。

设计目标：

- **stats 永远开**：即使 `--trace` 未开启，也应输出统计指标（至少包含 v1 最小集合）
- **trace summary 可选**：仅在 `--trace` 开启时输出汇总计数，为后续“教学模式/可解释性”扩展保留铺垫
- Trace summary 记录应轻量且易持久化

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

v1 目前仅输出 summary：

```json
{
  "enabled": true,
  "mode": "summary",
  "counts": {
    "choose_cell": 42,
    "assign": 81,
    "unassign": 40,
    "contradiction": 85,
    "solution_found": 1
  }
}
```

### 字段约定

- `enabled`：是否开启 trace（由 CLI 参数决定）
- `mode`：当前仅允许 `summary`
- `counts`：事件类型 -> 次数（详见 `Tracer` 实现）

> 逐步 `steps` 输出将在后续“教学模式”里重新引入；若要恢复，需要先更新本设计文档与 CLI 契约。

## CLI 行为要求（与 trace 相关）

- 默认：`--trace` 关闭，仅输出 `stats`（以及 `status/solution`）
- `--trace`：开启 summary，并在结果 JSON 中输出 `trace.enabled=true`、`mode=summary`
- `--trace-file <path>`：将 summary 写入文件；若未指定，则写入 `var/traces/<puzzle>.<timestamp>.trace.json`
  - 目录 `var/` 已在仓库 `.gitignore` 中忽略，可安全存放运行产物

具体参数名与帮助文本以 README 为准。
