from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path


def ensure_venv_python() -> None:
    base_dir = Path(__file__).resolve().parent
    repo_root = base_dir.parents[1]
    venv_python = repo_root / ".venv" / "Scripts" / "python.exe"
    current_python = Path(sys.executable).resolve()

    if venv_python.exists() and current_python != venv_python.resolve():
        os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve())])


def main() -> None:
    ensure_venv_python()
    from cadquery import exporters

    base_dir = Path(__file__).resolve().parent
    repo_root = base_dir.parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    out_dir = base_dir / "exports" / "step"
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx in range(1, 11):
        module = importlib.import_module(f"cadquery_models.pt01.part_{idx:02d}")
        output_path = out_dir / f"part_{idx:02d}.step"
        exporters.export(module.result, str(output_path))
        print(f"exported: {output_path}")


if __name__ == "__main__":
    main()
