# Repository Guidelines

## Project Structure & Module Organization
- `src/` — Sudoku solver code: prefer modules like `board/`, `solver/`, `strategies/`, `io/`.
- `tests/` — Unit tests mirroring `src/` layout (e.g., `tests/solver/test_backtracking.py`).
- `examples/` — Small runnable demos (CLI inputs, sample puzzles).
- `data/` — Static assets (puzzle files). Keep under version control if small.
- `scripts/` — One-off tooling (e.g., generation, benchmarking).

## Build, Test, and Development Commands
- Preferred env manager: `uv` (over `venv`).
- Create env + install deps: `uv venv && source .venv/bin/activate && uv pip install -r requirements.txt`.
- Run tests: `uv run pytest -q` (optionally `uv run pytest --maxfail=1 --disable-warnings`).
- Lint/format: `uvx ruff check . && uvx ruff format .` or `uvx black . && uvx isort .`.
- Local run (example): `uv run python -m src.cli --input data/puzzles/easy.txt`.
- If a `Makefile` exists, prefer: `make install`, `make test`, `make fmt`, `make lint`.

## Coding Style & Naming Conventions
- Python: 4-space indent, PEP 8, type hints required for public APIs.
- Names: modules `snake_case`, classes `CamelCase`, functions/vars `snake_case`.
- Keep files focused; avoid >300 lines per module when practical.
- Pure logic in `src/`; keep I/O, CLI, and examples separate.

## Testing Guidelines
- Framework: `pytest` with `tests/` mirroring `src/` paths.
- Test names: files `test_*.py`; functions `test_*` with clear Arrange/Act/Assert.
- Coverage: target ≥90% for `solver/` and `strategies/`; include edge cases (unsolvable, multiple solutions, minimal clues).
- Property-based tests (optional): `hypothesis` for board invariants.

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
- Commits should be small and focused; include rationale in body if non-trivial.
- PRs must include: summary, linked issue (if any), before/after notes, and test coverage for changes.
- CI green before review; no failing or skipped tests without justification.

## Language & Interaction
- Global rule: use Simplified Chinese for all user-facing interaction (CLI prompts, flags/help, error messages, user-facing logs, README examples).
- Keep code in English: identifiers, comments, and docstrings remain English.
- If helpful, keep short bilingual labels; otherwise Chinese outside code, English inside code.
- Example: `print("请输入数独谜题文件路径：")  # Request input file path`

## Security & Configuration Tips
- Determinism: avoid hidden globals; pass RNG/seed explicitly for reproducible benchmarks.
- Data safety: do not commit large datasets; use `.gitignore` for generated files.
- No network access required; solvers must run offline.
