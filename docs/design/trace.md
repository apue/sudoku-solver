# Trace / Stats（v1）

本文件定义 v1 的统计（Stats）与可选步骤记录（Trace Steps）契约。

设计目标：

- **stats 永远开**：即使 `--trace` 未开启，也应输出统计指标（至少包含 v1 最小集合）
- **trace steps 可选**：仅在 `--trace` 开启时输出步骤列表，用于后续“教学模式/可解释性”扩展
- Trace 记录应尽量轻量，避免显著拖慢求解

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

建议输出结构（JSON）：

```json
{
  "enabled": true,
  "steps": [
    { "type": "CHOOSE_CELL", "cell": [1, 1], "depth": 0, "reason": "first_empty" },
    { "type": "ASSIGN", "cell": [1, 1], "value": 5, "depth": 0, "reason": "try_value" },
    { "type": "CONTRADICTION", "cell": [1, 3], "depth": 3, "reason": "row_duplicate" },
    { "type": "UNASSIGN", "cell": [1, 1], "value": 5, "depth": 0, "reason": "backtrack" }
  ]
}
```

### 字段约定

- `enabled`：是否开启 trace（由 CLI 参数决定）
- `steps`：步骤列表；若未开启 trace，可省略或输出空列表

每个 step 建议字段：

- `type`：枚举字符串（建议最小集合：`CHOOSE_CELL | ASSIGN | UNASSIGN | CONTRADICTION | SOLUTION_FOUND`）
- `cell`：坐标二元组 `[row, col]`，**1-based**（为了用户更直观；内部实现可用 0-based）
- `value`：仅在 `ASSIGN/UNASSIGN` 时存在（1..9）
- `depth`：当前深度（实现自定义，但要一致）
- `reason`：简短原因标识（英文短语即可，便于后续国际化/映射自然语言）

## CLI 行为要求（与 trace 相关）

- 默认：`--trace` 关闭，仅输出 `stats`（以及 `status/solution`）
- `--trace`：开启 trace 并在结果 JSON 中输出 `trace.enabled=true` 与 `steps`
- `--trace-file <path>`：将 trace（建议仅 trace 部分或完整结果，二选一并写清）输出到文件
  - 建议 v1：**stdout 始终输出完整结果 JSON**；若指定 `--trace-file`，则额外将 `trace`（或完整结果）写入文件

具体参数名与帮助文本以 README 为准。
