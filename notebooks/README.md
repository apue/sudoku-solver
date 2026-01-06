# Notebook Guide

本目录存放用于可视化策略推理的 Notebook。建议步骤：

1. 安装依赖：`uv pip install ipywidgets ipycanvas`（或在 VS Code / JupyterLab 中启用内置支持）。
2. 启动 `jupyter lab` 或 `jupyter notebook`，打开 `policy_explorer.ipynb`。
3. 修改 `puzzle_path` / `policy` / `strategy_override`，运行最后一个单元即可看到交互式控件。

Notebook 基于 `sudoku_solver.notebook.visualizer` 提供的 API：

- `solve_for_notebook(path, policy)`：返回策略步骤、状态序列与 metrics。
- `build_policy_explorer(path, policy)`：返回 ipywidgets 组件，可逐步回放策略。

> Notebook 渲染不会写入数据库或 trace 文件，可安全在本地运行。
