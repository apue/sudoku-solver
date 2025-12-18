```sql```
CREATE TABLE IF NOT EXISTS results (
    -- 基本标识
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_case_id TEXT NOT NULL,          -- 例如文件名：002.json
    method TEXT NOT NULL,                -- 例如：bt, bt+s1, bt+s1+s2

    -- 结果状态
    status TEXT NOT NULL,                -- unique / multiple / unsat
    solutions_found INTEGER NOT NULL,

    -- 搜索规模（Search Cost）
    assignments INTEGER NOT NULL,
    backtracks INTEGER NOT NULL,
    contradictions INTEGER NOT NULL,

    -- 搜索深度（Search Depth）
    max_depth INTEGER NOT NULL,

    -- 推理 vs 猜测（Inference vs Guessing）
    num_guess_points INTEGER NOT NULL,
    first_guess_depth INTEGER,            -- nullable
    deduced_assignments INTEGER NOT NULL,
    guessed_assignments INTEGER NOT NULL,

    -- 可选：运行信息
    time_ms INTEGER,                      -- 可为空，v1 可先不填
    created_at TEXT NOT NULL              -- ISO-8601 字符串
);
```
