# 架构总览（v1）

本项目 v1 目标：实现**标准 9×9 数独**求解（纯回溯），并输出结构化的 `stats`（常开）与 `trace`（可选），为后续“教学模式/规则系统”打基础。

## 范围（v1）

包含：

- 标准 9×9 数独约束：行/列/3×3 宫
- 回溯求解：区分 `unique / multiple / unsat`
- `verify`：验证给定 puzzle 与 solution 的合法性
- `stats`：始终输出（例如回溯次数、递归调用数）
- `trace`：默认关闭，`--trace` 打开

不包含：

- 候选集推理（naked/hidden single 等）
- 高级规则系统（pairs / x-wing 等）
- OCR / Web / Mobile UI
- 性能极致优化（例如 DLX / SAT 等）

## 模块划分（建议）

- `board/`：盘面与基础工具（校验、取行列宫、坐标等）
- `solver/`：求解器实现（v1：`backtracking`）
- `verify/`：验证器（可作为独立命令）
- `io/`：读写 JSON（输入 IR 与输出 schema）
- `trace/`：统计与可选步骤流（cross-cutting）
- `cli/`：命令行入口（用户交互中文、代码标识英文）

## 数据流

```
input.json -> io.load_puzzle -> board.Grid
           -> solver.solve (with tracer)
           -> SolveResult(status, solution?, stats, trace?)
           -> io.dump_result -> stdout / file
```

## 依赖方向（强约束）

- `cli` 可以依赖 `io/solver/verify/trace/board`
- `solver` 可以依赖 `board/trace`（但不得依赖 `cli/io`）
- `verify` 可以依赖 `board`（可依赖 `io` 仅用于文件装载；或由 `cli` 统一装载）
- `trace` 不得依赖其它业务模块（只做记录/序列化）
