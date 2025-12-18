PYTHON ?= 3.11

.PHONY: help sync lint fmt test ci run-solve run-verify

help:
	@echo "Targets: sync lint fmt test ci run-solve run-verify"

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

