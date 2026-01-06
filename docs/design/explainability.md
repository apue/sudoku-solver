# Explainability / Notebook API（v2）

v2 已输出策略步骤 schema，可直接供 v3 Notebook/Web UI 消费。接口约定：

- CLI：`uv run sudoku-solver solve puzzle.json --trace --trace-mode steps`
- `trace.strategy_steps[]`：数组元素结构如下：

```json
{
  "strategy": "pointing",
  "depth": 5,
  "description": "r1c1, r1c2 限制 5 在同一行",
  "assignments": [
    {"cell": [1, 3], "value": 4, "reason": "unit_unique", "note": null}
  ],
  "eliminations": [
    {"cell": [1, 5], "values": [5], "reason": "pointing_row", "note": null}
  ],
  "metadata": {"value": 5, "unit": "row"}
}
```

消费方式：

1. `assignments`：渲染“填充动作”（高亮 cell、展示 value/原因）。
2. `eliminations`：渲染“候选删除”（可在 UI 上灰掉对应候选）。
3. `metadata`：可显示策略参数（如 value/宫/行列），或在 Notebook 中生成文字解释。
4. `depth`：与回溯深度对应，可用于构造时间线。

> 若仅需统计，可读取 `trace.strategy_counts` 或 `metrics["strategy_hits"]`。
>
> Notebook / Web UI 可直接加载 CLI 输出 JSON，无需额外 API。

## Notebook Helper

- 模块：`sudoku_solver.notebook.visualizer`
- `solve_for_notebook(path, policy)`：返回 `NotebookRun(states, steps, metrics)`，方便 Notebook 缓存数据。
- `build_policy_explorer(path, policy, notebook_run=None)`：生成 ipywidgets 控件（步骤 Slider + 策略过滤 + 候选高亮）。
- 示例 Notebook：`notebooks/policy_explorer.ipynb`。
