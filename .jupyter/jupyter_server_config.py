"""Project-local Jupyter Server config to keep notebooks clean on save."""
from __future__ import annotations


def _strip_output_pre_save(model, **kwargs) -> None:
    if model.get("type") != "notebook":
        return
    content = model.get("content")
    if not content:
        return
    for cell in content.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        cell["outputs"] = []
        cell["execution_count"] = None


c = get_config()
c.FileContentsManager.pre_save_hook = _strip_output_pre_save
