# I/O 契约（v1）

本文件定义 v1 的输入/输出 JSON 契约。任何 CLI 行为、示例、测试与实现都必须与本文件一致；如需变更，先改本文档，再改代码。

## 输入（Puzzle JSON）

文件格式：

```json
{
  "grid": [
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0]
  ]
}
```

约束：

- `grid` 必须是 9×9 的二维数组
- 每个元素必须是整数 `0..9`
- `0` 表示空格；`1..9` 表示给定数（givens）
- givens 允许为 0 个或多个，但必须满足基本合法性（不与标准数独约束冲突）
  - 若 givens 冲突，CLI 应返回清晰错误（中文），并以非 0 退出码结束

## 输出（Solve Result JSON）

整体格式（字段顺序不作强制要求）：

```json
{
  "status": "unique",
  "solution": [[...9], ... 9],
  "stats": { "calls": 0, "backtracks": 0, "assignments": 0, "max_depth": 0 },
  "trace": { "enabled": false, "steps": [] }
}
```

字段说明：

### `status`

枚举值：

- `unique`：唯一解
- `multiple`：多解（≥2）。实现需能检测到“至少两个解”，并输出任意一个解到 `solution`
- `unsat`：无解。此时 `solution` 必须为 `null`

### `solution`

- 当 `status` 为 `unique` 或 `multiple`：必须是 9×9 二维数组，元素为 `1..9`
- 当 `status` 为 `unsat`：必须为 `null`

### `stats`（始终存在）

见 `docs/design/trace.md` 中的 `Stats` 字段定义（v1 至少包含：`calls/backtracks/assignments/max_depth`）。

### `trace`（可选）

- 默认（未开启 `--trace`）：可以省略 `trace` 字段，或输出 `trace.enabled=false`
- 开启 `--trace`：必须输出 `trace.enabled=true` 且包含 `steps`（详见 `docs/design/trace.md`）

## 示例文件约定（建议）

- `examples/puzzle_*.json`：输入 puzzle
- `examples/solution_*.json`：仅包含 `solution`（用于 `verify --solution`），格式建议：

```json
{ "grid": [[...9], ... 9] }
```

