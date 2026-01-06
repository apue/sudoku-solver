# 回溯求解语义（v2）

本文件定义 v1/v1.1 的回溯求解器语义与“多解检测”口径，并扩展 v2 的策略 policy runner。v2 在回溯之前引入 `strategies/`（naked/hidden single、naked pair、pointing、claiming），通过策略 policy 配置化启用，并输出结构化 `StrategyStep`，以支撑 v3 可解释性和策略对比。

## 支持范围

- 仅支持标准 9×9 数独（行/列/3×3 宫）
- 输入来自 `docs/design/io.md` 定义的 Puzzle JSON

## 求解目标与返回

求解器输出 `SolveResult`，其 JSON 形式见 `docs/design/io.md`。

- 若存在且仅存在 1 个解：`status=unique`，输出该解
- 若存在 ≥2 个解：`status=multiple`，输出其中任意一个解（但必须证明“至少两个解”）
- 若不存在解：`status=unsat`，`solution=null`

## 多解检测策略（强制）

为避免枚举所有解，v1 采用“找前两个解”的策略：

- 在回溯搜索中，最多搜集 `max_solutions=2` 个不同完整解
- 若找到第 2 个解，则可立即停止搜索并返回 `status=multiple`
- 若搜索结束且找到 0 个解：`unsat`
- 若搜索结束且找到 1 个解：`unique`

> 备注：这是“至少两个解”的检测，不要求计算总解数。

## 策略 Runner（v2）

- `strategies/` 目录下定义一组策略：`naked_single`、`hidden_single`、`naked_pair`、`pointing`、`claiming`，统一实现 `Strategy.apply(context)`。
- `StrategyStep` schema：
  - `assignments[]`：`row/col/value/reason/note`
  - `eliminations[]`：`row/col/values/reason/note`
  - `metadata`：任意附加信息（如 `value`, `unit`）。
- `StrategyRunner` 根据 policy 顺序调用策略：policy 通过 `--policy <name>`（默认 `default`）或 `--strategies a,b,...`（自定义顺序）配置。
- 每次策略命中后，solver 应：
  - `Recorder.strategy.step(step, depth)` 记录，与 trace/metrics 解耦
  - 应用 eliminations：更新候选集；若出现空候选则立即判定矛盾
  - 应用 assignments：写入网格、递增 stats/metrics，并重新构建候选集
  - 重复直到无策略可进一步推进
- CLI `--compare-policy other`：使用相同 puzzle 连续跑两套 policy，输出 primary/comparison 结构，方便对比指标。

禁用策略：`--no-deductions` 或 `use_deductions=False` 时，solver 退回 v1 纯回溯，仅构建基础候选集（供 MRV 选择与 trace 使用）。

## 候选集与 MRV

- 调用 `strategies.candidates.build_candidate_map(grid)` 构建 `(row, col) -> 候选集合`。
- 策略消除/赋值直接作用于此候选 map；当策略执行完毕，`_search` 阶段仍可使用该 map 选择“最少候选”的格子（MRV）并按候选顺序尝试。
- 候选 map 始终反映“当前网格状态 + 已知策略 eliminations”，是策略与回溯的共享状态。

## 回溯搜索（行为要求）

- 深度优先（DFS）即可
- 每一步选择一个尚未赋值的格子，并尝试赋值 `1..9`
- 在尝试赋值时必须检测局部一致性：
  - 当前行/列/宫不得出现重复数字
  - 发现冲突则回退（backtrack）
- 当所有格子都已赋值且无冲突：得到一个完整解

## Stats（统计口径）

`stats` 必须至少包含（名称可固定为以下英文字段）：

- `calls`：递归调用次数（或“节点访问次数”）——每进入一次搜索函数记一次
- `assignments`：尝试赋值次数（对某个格子写入一个候选值的尝试）
- `backtracks`：回退次数（一次赋值尝试导致失败并撤销）
- `max_depth`：搜索达到的最大深度（已赋值格子数或递归深度均可，但需在实现中解释一致的口径）

更完整字段见 `docs/design/trace.md`。
