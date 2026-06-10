from __future__ import annotations

"""导出 15 齿、模数 2 的直齿轮 STEP 模板。

使用方式：
    .venv\\Scripts\\python.exe cadquery_models\\example\\test_step\\export_gear_m2_z15.py

运行后会在当前目录下的 exports 文件夹中生成 STEP 文件。
"""

from pathlib import Path
import sys

import cadquery as cq


# 让脚本可以直接导入 example 目录中的齿轮建模模块
CURRENT_DIR = Path(__file__).resolve().parent
EXAMPLE_DIR = CURRENT_DIR.parent
if str(EXAMPLE_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLE_DIR))

from gear_generator import SpurGearSpec, build_spur_gear


# =========================
# 可直接修改的齿轮参数
# =========================

# 模数 m
MODULE = 1

# 齿数 z
TOOTH_COUNT = 15

# 齿轮厚度 b，单位 mm
THICKNESS = 10.0

# 中心孔直径，单位 mm
BORE_DIAMETER = 5

# 压力角 alpha，单位 deg
PRESSURE_ANGLE_DEG = 20.0

# 侧隙 backlash，单位 mm
BACKLASH = 0.1

# 齿顶高系数 ha*
ADDENDUM_COEFFICIENT = 1.0

# 齿根高系数 hf*
DEDENDUM_COEFFICIENT = 1.25


# =========================
# 曲线离散参数
# 数值越大，曲线越细，但生成会稍慢
# =========================
INVOLUTE_SAMPLES = 24
TIP_ARC_SAMPLES = 12
ROOT_ARC_SAMPLES = 8


def build():
    """构建当前参数对应的齿轮实体。"""
    spec = SpurGearSpec(
        module=MODULE,
        tooth_count=TOOTH_COUNT,
        thickness=THICKNESS,
        pressure_angle_deg=PRESSURE_ANGLE_DEG,
        addendum_coefficient=ADDENDUM_COEFFICIENT,
        dedendum_coefficient=DEDENDUM_COEFFICIENT,
        bore_diameter=BORE_DIAMETER,
        backlash=BACKLASH,
    )
    return build_spur_gear(
        spec,
        involute_samples=INVOLUTE_SAMPLES,
        root_arc_samples=ROOT_ARC_SAMPLES,
        tip_arc_samples=TIP_ARC_SAMPLES,
    )


def export_step() -> Path:
    """导出 STEP 文件并返回导出路径。"""
    result = build()
    export_dir = CURRENT_DIR / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = export_dir / "gear_2.step"
    cq.exporters.export(result, str(export_path))
    return export_path


def main():
    export_path = export_step()
    print(f"exported: {export_path}")


if __name__ == "__main__":
    main()

