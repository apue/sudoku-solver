# Roadmap

> 日期以里程碑为准，不在 v1 承诺具体时间。

## v1：回溯求解 + 多解/无解 + stats/trace 基础

Done 标准：

- 支持标准 9×9 输入：`docs/design/io.md`
- CLI：`solve` 与 `verify`
- `solve` 输出：
  - `status=unique`：输出解
  - `status=multiple`：能检测到“至少两个解”，并输出任意一个解
  - `status=unsat`：明确无解，`solution=null`
- `stats` 始终输出（至少 `calls/assignments/backtracks/max_depth`）
- `trace` 默认关闭；`--trace` 开启步骤输出；`--trace-file` 可写文件
- `verify` 能验证 solution 合法且不违背 givens
- CI 绿：ruff + pytest（由仓库实际 workflow 定义）

## v1.1：候选集 + 单元唯一（更像人类推理）

- 候选初始化 + 传播
- `naked_single` / `hidden_single`
- 在不回溯的情况下尽量推进；卡住再回溯
- stats 增加：`deductions` / `guesses`

## v2：规则系统 + policy 对比

- 引入 `strategies/` 目录（pairs、pointing、claiming…）
- policy 配置化（启用策略集合 + 顺序）
- benchmark 脚本与题库格式
- 输出对比指标与可视化（先 CSV，再考虑图表）

## v3：可解释性（教学模式）

- 将 `trace.steps` 映射为更友好的中文解释
- UI（先 notebook/terminal 渲染，再 web）

## v4：Web / Mobile（本地运行）

- Web：拖拽 JSON -> 本地求解（Web Worker）
- Mobile：本地求解 + 结果回放

## v5：OCR

- 网格定位、切格、数字识别 -> 生成 IR（`grid`）
- 与 solver 解耦：OCR 只负责产出 `docs/design/io.md` 的输入格式
