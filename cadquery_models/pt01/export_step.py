from __future__ import annotations

import importlib
import sys
from pathlib import Path

from cadquery import exporters


def main() -> None:
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
