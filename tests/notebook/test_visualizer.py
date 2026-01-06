from __future__ import annotations

import pytest

from sudoku_solver.notebook.visualizer import resolve_project_root, solve_for_notebook


def test_solve_for_notebook_produces_states(positive_puzzle_path):
    run = solve_for_notebook(positive_puzzle_path, policy="human-lite")
    assert run.states, "should capture at least initial state"
    assert len(run.states) == len(run.steps) + 1
    assert run.steps[0].strategy in {"naked_single", "hidden_single"}


def test_solver_respects_strategy_override(positive_puzzle_path):
    run = solve_for_notebook(positive_puzzle_path, strategy_override=["naked_single"])
    assert all(step.strategy == "naked_single" for step in run.steps)


def test_render_widget_optional_dependency(positive_puzzle_path):
    pytest.importorskip("ipywidgets")
    pytest.importorskip("IPython")
    from sudoku_solver.notebook.visualizer import build_policy_explorer

    widget = build_policy_explorer(positive_puzzle_path, policy="human-lite")
    assert hasattr(widget, "children")


def test_resolve_project_root_finds_pyproject(tmp_path, monkeypatch):
    fake_root = tmp_path / "proj"
    fake_root.mkdir()
    (fake_root / "pyproject.toml").write_text("[build-system]\n")
    nested = fake_root / "notebooks"
    nested.mkdir()
    result = resolve_project_root(nested)
    assert result == fake_root
