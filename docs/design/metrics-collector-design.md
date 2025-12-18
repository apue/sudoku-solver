# Metrics 采集设计（事件驱动）

## 背景与目标
- 目标：在不绑定具体算法/策略的前提下，稳定地产出符合 `docs/metric.md` 的指标（metrics）。
- 原则：与 trace 解耦、与 solver/strategy 解耦；保持可扩展、可聚合、可解释。

## 设计原则
- 稳定契约：事件名与字段一经引入尽量不变；允许向后兼容扩展。
- 低侵入：solver/strategy 只需在关键点“发事件”，不直接触碰指标实现。
- 独立于 trace：metrics 始终可用；trace 仅用于教学展示。

## 组件与依赖
- Recorder（事件分发器）：提供统一的事件 API，转发到多个 sink。
- Sinks（接收器）：
  - MetricsCollector（常开）：将事件聚合为 metrics 对象。
  - Tracer（可选）：steps 或 summary，两者仅做可视化/教学。
- 依赖方向：`solver/strategies -> Recorder -> {MetricsCollector, Tracer}`。Collector 不依赖 solver 细节。

## 事件模型（API）
- decision.choose_cell(r, c, depth)
- decision.guess_point(depth)
- attempt.assign(r, c, v, source: "guess" | "deduced")
- attempt.contradiction(r, c, v? = None, reason = "invalid_candidate")
- state.unassign(r, c, v, reason = "backtrack")
- search.update_depth(depth)
- result.solution_found()

说明：
- 坐标采用内部 0-based；Tracer 可转换为 1-based 呈现。
- depth 为当前决策深度；由 solver 负责传入。
- source 表示赋值来源：确定性推理（deduced）或搜索尝试（guess）。

## MetricsCollector 行为（v1）
- assignments：统计 attempt.assign 次数（任意 source）。
- backtracks：统计 state.unassign(reason=backtrack)。
- contradictions：统计 attempt.contradiction 次数。
- max_depth：取 search.update_depth 的最大值。
- num_guess_points：统计 decision.guess_point 次数。
- first_guess_depth：首次 guess_point 的 depth，之后不再覆盖；无猜测为 null。
- deduced_assignments：统计 attempt.assign(source=deduced)。
- guessed_assignments：统计 attempt.assign(source=guess)。
- solutions_found：统计 result.solution_found 次数（0/1/2）。
- status：由 solver 最终返回并写入输出，与 metrics 一并展示。

## 输出 Schema（顶层 metrics 字段）
示例（见 `docs/metric.md`）：
```json
{
  "status": "unique",
  "assignments": 0,
  "backtracks": 0,
  "contradictions": 0,
  "max_depth": 0,
  "num_guess_points": 0,
  "first_guess_depth": null,
  "deduced_assignments": 0,
  "guessed_assignments": 0,
  "solutions_found": 0
}
```

## 使用方式（伪代码）
```python
rec = Recorder(sinks=[MetricsCollector(), Tracer(enabled=flag, mode=mode)])
# 选择下一个空格
depth = ...
rec.decision.choose_cell(r, c, depth)
rec.decision.guess_point(depth)  # 纯回溯：每个选择点都是猜测点
# 尝试赋值
rec.attempt.assign(r, c, v, source="guess")  # 推理型策略则用 source="deduced"
# 无效候选
rec.attempt.contradiction(r, c, v, reason="invalid_candidate")
# 回退
rec.state.unassign(r, c, v, reason="backtrack")
# 深度更新
rec.search.update_depth(depth)
# 找到完整解
rec.result.solution_found()
# 结束后在 CLI 侧：metrics = metrics_collector.finalize()
```

## 扩展与版本化
- 允许新增事件（如 `rule_applied(name)`、`branching(candidates=n)`），Collector 可选择忽略或增量消费。
- 允许新增可选 metrics 字段（v1.1+），不破坏现有聚合与对比。

## 迁移与兼容
- 现有 trace 步骤/summary 保持不变；仅新增 Recorder & MetricsCollector。
- solver 逐步将内部计数替换为事件发射；不强制一次完成。
- CLI 在 solve 结果顶层新增 `metrics` 字段；verify 无需改动。

