"""JSON I/O contract helpers (skeleton)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_puzzle(path: str | Path) -> Dict[str, Any]:
    """Load a puzzle JSON into a dict (no validation in skeleton)."""
    return json.loads(Path(path).read_text())


def dump_result(obj: Dict[str, Any], path: str | Path) -> None:
    """Write result JSON to a file using UTF-8 without ASCII escaping."""
    Path(path).write_text(json.dumps(obj, ensure_ascii=False))
