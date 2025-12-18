PYTHON ?= 3.11
FILE ?= data/001.json
OUT ?= /tmp/solve_out.json
SOL ?= /tmp/solution.from_solve.json
TRACE_FILE ?= /tmp/trace.json

.PHONY: help bootstrap sync lint fmt test ci run-solve run-verify e2e db.init db.last db.export db.purge

help:
    @echo "Targets: bootstrap sync lint fmt test ci run-solve run-verify e2e db.init db.last db.export db.purge"
    @echo "Vars: FILE=<puzzle json> (default: data/001.json), TRACE=1 to enable trace"

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

# End-to-end: solve -> write solution file -> verify
# Usage: make e2e [FILE=data/001.json] [TRACE=1]
e2e:
	# 1) Solve with summary; capture only to file
	uv run sudoku-solver solve "$(FILE)" --trace-summary > "$(OUT)"
	# 2) Extract solution grid to a temp file for verify
	uv run python -c 'import json,sys; out,sol=sys.argv[1:3]; obj=json.load(open(out)); g=obj.get("solution"); import sys as _s; (_s.exit(3)) if not g else json.dump({"grid": g}, open(sol,"w"))' "$(OUT)" "$(SOL)"
	# 3) Verify and ensure ok==true
	uv run sudoku-solver verify "$(FILE)" --solution "$(SOL)" > /tmp/verify_out.json
	uv run python -c 'import json,sys; ok=json.load(open("/tmp/verify_out.json")).get("ok",False); import sys as _s; _s.exit(0) if ok else (_s.stderr.write("verify failed\n"), _s.exit(2))'
	# 4) On success, pretty-print solution matrix, metrics and trace summary
	uv run python -c 'import json,sys; obj=json.load(open(sys.argv[1])); print("== Solution =="); [print(json.dumps(r, ensure_ascii=False)) for r in obj.get("solution", [])]; met=obj.get("metrics") or {}; print("== Metrics =="); keys=["assignments","backtracks","contradictions","max_depth","num_guess_points","first_guess_depth","deduced_assignments","guessed_assignments","solutions_found"]; [print(f"{k}: {met.get(k)}") for k in keys]; tr=obj.get("trace") or {}; print("== Trace Summary =="); print("\n".join([f"{k}: {v}" for k,v in (tr.get("counts") or {}).items()])) if tr.get("mode")=="summary" and "counts" in tr else print("(no summary; enable with --trace-summary)")' "$(OUT)"

# --- DB helpers (SQLite) ---
DB_PATH ?= var/results.sqlite3

db.init:
	@mkdir -p var
	@sqlite3 "$(DB_PATH)" 'CREATE TABLE IF NOT EXISTS results ( id INTEGER PRIMARY KEY AUTOINCREMENT, test_case_id TEXT NOT NULL, method TEXT NOT NULL, status TEXT NOT NULL, solutions_found INTEGER NOT NULL, assignments INTEGER NOT NULL, backtracks INTEGER NOT NULL, contradictions INTEGER NOT NULL, max_depth INTEGER NOT NULL, num_guess_points INTEGER NOT NULL, first_guess_depth INTEGER, deduced_assignments INTEGER NOT NULL, guessed_assignments INTEGER NOT NULL, time_ms INTEGER, created_at TEXT NOT NULL );'
	@echo "initialized $(DB_PATH)"

db.last:
	@echo "Showing last 10 rows from $(DB_PATH)"
	@sqlite3 -header -column "$(DB_PATH)" 'SELECT id, test_case_id, method, status, assignments, backtracks, max_depth, solutions_found, created_at FROM results ORDER BY id DESC LIMIT 10;'

db.export:
	@echo "Exporting CSV to /tmp/results_export.csv"
	@sqlite3 -header -csv "$(DB_PATH)" 'SELECT * FROM results ORDER BY id DESC;' > /tmp/results_export.csv
	@echo "/tmp/results_export.csv"

db.purge:
	@rm -f "$(DB_PATH)"
	@echo "purged $(DB_PATH)"
