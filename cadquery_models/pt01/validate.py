from __future__ import annotations

"""快速对比重建零件与原始 STL 的包围盒尺寸。"""

import importlib
import struct
import sys
from pathlib import Path

import numpy as np


def stl_bbox_mm(path: Path) -> np.ndarray:
    # 原始 STL 以米为单位导出，这里先统一换算成毫米再比较。
    data = path.read_bytes()
    tri_count = struct.unpack("<I", data[80:84])[0]
    arr = np.frombuffer(
        data,
        dtype=np.dtype([("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attr", "<u2")]),
        offset=84,
        count=tri_count,
    )
    vertices = arr["vertices"].reshape(-1, 3) * 1000.0
    return vertices.max(axis=0) - vertices.min(axis=0)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo_root))
    root = repo_root / "data-bin" / "pt01"
    # 逐个导入重建脚本，并将最终实体的包围盒与 STL 参考值对比。
    for idx in range(1, 11):
        module = importlib.import_module(f"cadquery_models.pt01.part_{idx:02d}")
        rebuilt_bbox = module.result.val().BoundingBox()
        rebuilt = np.array([rebuilt_bbox.xlen, rebuilt_bbox.ylen, rebuilt_bbox.zlen])
        reference = stl_bbox_mm(root / f"{idx}.stl")
        delta = rebuilt - reference
        print(
            f"part_{idx:02d}",
            "rebuilt",
            np.round(rebuilt, 3),
            "stl",
            np.round(reference, 3),
            "delta",
            np.round(delta, 3),
        )


if __name__ == "__main__":
    main()
