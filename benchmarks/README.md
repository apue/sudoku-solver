# Benchmarks

`v2` 引入策略 policy 对比，需要一个简单的基准数据集：

- Puzzle 文件：沿用 `data/*.json`，也可以在 `benchmarks/` 目录下放置额外 JSON。
- 命令：`python scripts/policy_benchmark.py --puzzles data/001.json data/002.json --policies human-lite default aggressive`
- 输出：默认写入 `var/benchmarks/benchmark.<timestamp>.csv`，可通过 `--output` 指定。

CSV 字段：`puzzle, policy, status, time_ms, assignments, backtracks, deduced_assignments, num_guess_points`。

> `var/benchmarks/` 已在 `.gitignore` 中忽略，可安全存放运行产物。
