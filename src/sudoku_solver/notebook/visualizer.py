"""Helpers for building interactive Sudoku notebooks using ipywidgets."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from sudoku_solver.board.grid import Grid
from sudoku_solver.io.json_io import load_puzzle
from sudoku_solver.solver.backtracking import solve_backtracking
from sudoku_solver.strategies.candidates import build_candidate_map

Coord = Tuple[int, int]
CandidateMap = Dict[Coord, set[int]]


@dataclass
class StrategyAssignment:
    row: int
    col: int
    value: int


@dataclass
class StrategyElimination:
    row: int
    col: int
    values: List[int]


@dataclass
class StrategyStepPayload:
    index: int
    strategy: str
    description: str
    assignments: List[StrategyAssignment]
    eliminations: List[StrategyElimination]
    metadata: Dict[str, object]


@dataclass
class BoardState:
    index: int
    grid: List[List[int]]
    candidates: CandidateMap
    last_step: Optional[StrategyStepPayload]


@dataclass
class NotebookRun:
    puzzle_path: Path
    policy: str
    metrics: Dict[str, object]
    trace: Dict[str, object]
    steps: List[StrategyStepPayload]
    states: List[BoardState]
    elapsed_ms: int

    @property
    def available_strategies(self) -> List[str]:
        return sorted({step.strategy for step in self.steps})


def resolve_project_root(start: Optional[Path] = None) -> Path:
    """Walk parent directories to locate the repository root (pyproject.toml)."""
    path = start or Path.cwd()
    for candidate in [path, *path.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return path


def _load_strategy_steps(trace: Dict[str, object]) -> List[StrategyStepPayload]:
    raw_steps: Iterable[Dict[str, object]] = trace.get("strategy_steps", []) if trace else []
    parsed: List[StrategyStepPayload] = []
    for idx, step in enumerate(raw_steps):
        assignments = [
            StrategyAssignment(row=cell[0] - 1, col=cell[1] - 1, value=item["value"])
            for item in step.get("assignments", [])
            for cell in [tuple(item["cell"])]
        ]
        eliminations = [
            StrategyElimination(
                row=cell[0] - 1,
                col=cell[1] - 1,
                values=list(item.get("values", [])),
            )
            for item in step.get("eliminations", [])
            for cell in [tuple(item["cell"])]
        ]
        parsed.append(
            StrategyStepPayload(
                index=idx + 1,
                strategy=step.get("strategy", "unknown"),
                description=step.get("description", ""),
                assignments=assignments,
                eliminations=eliminations,
                metadata=step.get("metadata", {}) or {},
            )
        )
    return parsed


def _copy_grid_cells(grid: Grid) -> List[List[int]]:
    return [row[:] for row in grid.cells]


def _build_states(base_grid: Grid, steps: List[StrategyStepPayload]) -> List[BoardState]:
    working = base_grid.clone()
    states: List[BoardState] = []
    states.append(
        BoardState(
            index=0,
            grid=_copy_grid_cells(working),
            candidates=build_candidate_map(working),
            last_step=None,
        )
    )
    for step in steps:
        for assignment in step.assignments:
            working.set_cell(assignment.row, assignment.col, assignment.value)
        states.append(
            BoardState(
                index=step.index,
                grid=_copy_grid_cells(working),
                candidates=build_candidate_map(working),
                last_step=step,
            )
        )
    return states


def solve_for_notebook(
    puzzle_path: str | Path,
    *,
    policy: str = "human-lite",
    strategy_override: Optional[List[str]] = None,
) -> NotebookRun:
    """Run the solver with trace steps enabled for notebook visualization."""
    puzzle_file = Path(puzzle_path)
    if not puzzle_file.exists():
        project_root = resolve_project_root()
        candidate = project_root / puzzle_file
        if candidate.exists():
            puzzle_file = candidate
    grid = load_puzzle(puzzle_file)
    base_grid = grid.clone()
    import time

    t0 = time.perf_counter()
    result, metrics = solve_backtracking(
        grid,
        trace_enabled=True,
        trace_mode="steps",
        use_deductions=True,
        strategy_policy=policy,
        strategy_override=strategy_override,
    )
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    trace_obj = result.trace or {}
    steps = _load_strategy_steps(trace_obj)
    states = _build_states(base_grid, steps)
    return NotebookRun(
        puzzle_path=puzzle_file,
        policy=policy,
        metrics=metrics,
        trace=trace_obj,
        steps=steps,
        states=states,
        elapsed_ms=elapsed_ms,
    )


# Widget rendering helpers --------------------------------------------------


def _require_widgets():
    try:
        import ipywidgets as widgets
    except ModuleNotFoundError as exc:  # pragma: no cover - environment specific
        raise RuntimeError(
            "ipywidgets is required for notebook visualization. Install it via `pip install ipywidgets`."
        ) from exc
    return widgets


def _display_widget(widget):
    try:
        from IPython.display import display as ipy_display
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise RuntimeError(
            "IPython is required for notebook visualization. Install via `pip install ipython`."
        ) from exc
    ipy_display(widget)


def _format_candidate_grid(candidates: Iterable[int]) -> str:
    slots = [" "] * 9
    for v in candidates:
        if 1 <= v <= 9:
            slots[v - 1] = str(v)
    rows = ["".join(slots[i : i + 3]) for i in range(0, 9, 3)]
    return "\n".join(rows)


def _cell_html(value: int, candidates: Iterable[int], highlight: Optional[str]) -> str:
    base_style = "border:1px solid #999;height:40px;width:40px;display:flex;align-items:center;justify-content:center;font-size:20px;"
    empty_style = "font-size:12px;line-height:1.1;white-space:pre;text-align:center;font-family:'Courier New',monospace;"
    if highlight == "assign":
        base_style += "background-color:#e0ffe0;"
    elif highlight == "eliminate":
        base_style += "background-color:#ffe0e0;"
    if value:
        return f"<div style='{base_style}'><strong>{value}</strong></div>"
    cand_text = _format_candidate_grid(sorted(candidates))
    return f"<div style='{base_style}{empty_style}'>{cand_text}</div>"


def render_board_widget(state: BoardState, *, show_candidates: bool = True):
    """Render a board state as a ipywidgets grid."""
    widgets = _require_widgets()
    grid = widgets.GridspecLayout(9, 9, width="370px", height="370px")
    highlight_assign = {(a.row, a.col) for a in (state.last_step.assignments if state.last_step else [])}
    highlight_elim = {(e.row, e.col) for e in (state.last_step.eliminations if state.last_step else [])}
    for r in range(9):
        for c in range(9):
            key = (r, c)
            highlight = None
            if key in highlight_assign:
                highlight = "assign"
            elif key in highlight_elim:
                highlight = "eliminate"
            candidates = state.candidates.get(key, []) if show_candidates else []
            html = widgets.HTML(value=_cell_html(state.grid[r][c], candidates, highlight))
            grid[r, c] = html
    return grid


def build_policy_explorer(
    puzzle_path: str | Path,
    *,
    policy: str = "human-lite",
    strategy_override: Optional[List[str]] = None,
    show_candidates: bool = True,
    notebook_run: NotebookRun | None = None,
):
    """Return an ipywidgets UI for exploring solver steps."""
    widgets = _require_widgets()
    run = notebook_run or solve_for_notebook(
        puzzle_path,
        policy=policy,
        strategy_override=strategy_override,
    )
    total_steps = len(run.states) - 1

    slider = widgets.IntSlider(value=0, min=0, max=total_steps, description="步骤")
    strategy_options = ["全部"] + run.available_strategies
    strategy_dropdown = widgets.Dropdown(options=strategy_options, description="策略")
    next_button = widgets.Button(description="跳到下一个")
    board_output = widgets.Output(layout=widgets.Layout(border="none", overflow="visible"))
    text_output = widgets.Output()
    status_html = widgets.HTML()

    def _render(index: int) -> None:
        state = run.states[index]
        with board_output:
            board_output.clear_output(wait=True)
            _display_widget(render_board_widget(state, show_candidates=show_candidates))
        with text_output:
            text_output.clear_output(wait=True)
            if state.last_step is None:
                print("初始盘面")
            else:
                print(f"Step {state.last_step.index}/{total_steps}: {state.last_step.strategy}")
                if state.last_step.description:
                    print(state.last_step.description)
                if state.last_step.assignments:
                    coords = ", ".join(
                        f"r{a.row + 1}c{a.col + 1}={a.value}" for a in state.last_step.assignments
                    )
                    print("赋值:", coords)
                if state.last_step.eliminations:
                    elim = ", ".join(
                        f"r{e.row + 1}c{e.col + 1} - {''.join(str(v) for v in e.values)}" for e in state.last_step.eliminations
                    )
                    print("候选删除:", elim)

    def _on_slider(change):
        if change["name"] == "value":
            status_html.value = ""
            _render(change["new"])

    slider.observe(_on_slider)

    def _jump_to_next(_):
        start = slider.value + 1
        target_strategy = strategy_dropdown.value
        for idx in range(start, len(run.states)):
            step = run.states[idx].last_step
            if step is None:
                continue
            if target_strategy == "全部" or step.strategy == target_strategy:
                slider.value = idx
                return
        status_html.value = "<span style='color:#d00'>没有更多匹配的策略步骤。</span>"

    next_button.on_click(_jump_to_next)

    metrics_text = (
        f"策略：{run.policy} | 步数：{total_steps} | 耗时：{run.elapsed_ms} ms | "
        f"猜测次数：{run.metrics.get('num_guess_points', 0)}"
    )
    header = widgets.HTML(value=f"<strong>Sudoku Policy Explorer</strong><br>{metrics_text}")
    controls = widgets.HBox([slider, strategy_dropdown, next_button])
    container = widgets.VBox([header, controls, board_output, text_output, status_html])
    _render(0)
    return container
