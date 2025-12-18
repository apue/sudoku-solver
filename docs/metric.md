# Metrics Specification（实验指标规范）

## 1. 目的与原则

本项目的目标是构建一个**可解释的数独求解器（Sudoku Solver）**，而不是单纯追求解题速度。
因此，本指标体系的设计目标不是“谁更快”，而是回答以下问题：

- Solver 在多大程度上**依赖搜索（guess / backtracking）**
- 推理（deterministic inference）在多大程度上**减少了搜索空间**
- 不同 solver / strategy 配置之间，**搜索结构如何发生变化**
- 这些变化是否**可复现、可比较、可视化**

### 设计原则
1. **结构性优先于性能**：优先记录搜索结构，而不是时间。
2. **稳定契约**：指标字段一旦引入，应尽量长期保持不变。
3. **可聚合**：单次运行的结果必须可汇总为实验数据集。
4. **实现无关**：指标定义不绑定具体算法或优化细节。
5. **解释友好**：指标应能支持“为什么它更聪明”的解释。

---

## 2. 实验结果的基本单位

一次 **实验（Experiment Run）** 定义为：

> 在固定的输入谜题（puzzle）与固定的 solver 配置（config）下，  
> 执行一次完整求解过程，并收集一组指标。

每次运行应生成 **一份 metrics 结果对象**。

---

## 3. 指标分类总览

指标分为以下几类：

1. **搜索规模（Search Cost）**
2. **搜索深度（Search Depth）**
3. **推理 vs 猜测（Inference vs Guessing）**
4. **搜索分支特征（Branching Characteristics）**
5. **结果状态（Outcome）**
6. **运行环境（可选）**

并非所有指标都要求在 v1 实现，后文会标注优先级。

---

## 4. 核心指标（v1 必须支持）

### 4.1 搜索规模（Search Cost）

这些指标衡量 solver 探索了多大的搜索空间。

| 指标名 | 类型 | 含义 |
|------|------|------|
| `assignments` | int | 尝试进行赋值的总次数 |
| `backtracks` | int | 回溯（撤销赋值）的次数 |
| `contradictions` | int | 发现冲突（非法状态）的次数 |

#### 语义说明
- `assignments` 通常对应搜索树中访问的节点数量
- `backtracks` 反映搜索失败路径的数量
- `contradictions` 是“盲目搜索程度”的强信号

> 注：这些指标应独立于 trace 是否开启而始终统计。

---

### 4.2 搜索深度（Search Depth）

| 指标名 | 类型 | 含义 |
|------|------|------|
| `max_depth` | int | 搜索过程中达到的最大递归/决策深度 |

#### 语义说明
- 深度代表“最长猜测链”
- 推理能力越强，通常 `max_depth` 越小

---

### 4.3 推理 vs 猜测（Inference vs Guessing）

这是**可解释 solver 的核心指标组**。

| 指标名 | 类型 | 含义 |
|------|------|------|
| `num_guess_points` | int | 发生“必须猜测”的决策点数量 |
| `first_guess_depth` | int \| null | 第一次发生猜测时的深度 |
| `deduced_assignments` | int | 由确定性推理产生的赋值数量 |
| `guessed_assignments` | int | 由搜索分支产生的赋值数量 |

#### 语义说明
- **Guess Point**：指 solver 在无确定性推进手段时，选择一个分支进行尝试
- `first_guess_depth` 是“推理能力强弱”的直观指标
- 对于纯回溯 solver：
  - `deduced_assignments = 0`
  - `guessed_assignments = assignments`

---

## 5. 可选指标（v1.1 及以后）

### 5.1 搜索分支特征（Branching Characteristics）

| 指标名 | 类型 | 含义 |
|------|------|------|
| `avg_branching_factor` | float | 平均分支因子 |
| `max_branching_factor` | int | 最大分支因子 |

用于评估 heuristic / strategy 对“猜测质量”的影响。

---

### 5.2 时间与资源（谨慎使用）

| 指标名 | 类型 | 含义 |
|------|------|------|
| `time_ms` | int | 总运行时间（毫秒） |
| `cpu_time_ms` | int | CPU 时间 |

> 注意：时间类指标只应在**同一环境、同一实现**下用于辅助分析。

---

## 6. 结果状态（Outcome）

| 指标名 | 类型 | 含义 |
|------|------|------|
| `status` | enum | `unique` / `multiple` / `unsat` |
| `solutions_found` | int | 找到的解数量（通常为 0, 1, 或 2） |

---

## 7. 与 Trace 的关系

- **Metrics**：用于实验评估与对比，始终启用
- **Trace**：用于解释与教学，默认关闭

原则：
- Metrics 不依赖 trace 的开启
- Trace 可以引用 metrics，但不能反向依赖

---

## 8. 推荐的最小 Metrics Schema（v1）

v1 阶段，solver 至少应输出以下字段：

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
  "guessed_assignments": 0
}
