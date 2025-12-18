PYTHON ?= 3.11

.PHONY: help bootstrap sync lint fmt test ci run-solve run-verify

help:
	@echo "Targets: bootstrap sync lint fmt test ci run-solve run-verify"

# Ensure src/ package skeleton exists (for src/ layout packaging)
bootstrap:
	@[ -f src/sudoku_solver/__init__.py ] || \
	(mkdir -p src/sudoku_solver && \
	 echo '"""Sudoku Solver package"""' > src/sudoku_solver/__init__.py && \
	 echo 'bootstrapped src/sudoku_solver/__init__.py')

# Create/refresh env and install deps via uv
sync:
	uv sync

lint:
	uvx ruff check .

fmt:
	uvx ruff format .

test:
	uv run pytest -q

ci: lint test

# Example CLI runs (will require implementation of sudoku_solver/cli.py)
run-solve:
	uv run sudoku-solver solve examples/puzzle_easy.json --trace --trace-file trace.json

run-verify:
	uv run sudoku-solver verify examples/puzzle_easy.json --solution examples/solution_easy.json
