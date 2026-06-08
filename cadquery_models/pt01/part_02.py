from __future__ import annotations

"""零件 02：依据 STL 中截面高密度轮廓重建的带齿扇形板。"""

import cadquery as cq

try:
    from .common import extrude_profile, load_profile_points
except ImportError:
    from common import extrude_profile, load_profile_points


# 外齿轮廓来自预提取的 STL 中截面数据，运行时不会再读取 STL。
OUTER_PROFILE = load_profile_points(2)

THICKNESS = 4.0 #齿轮的厚度
CENTER_HOLE_DIAMETER = 8.5 #齿轮中轴的直径
CENTER_HOLE_POS = (0.225, -0.486) #齿轮中轴的位置
SMALL_HOLE_DIAMETER = 3.2 #齿轮上小孔的直径
SMALL_HOLE_POS = (10.410, -0.180) #齿轮上小孔的位置


def build() -> cq.Workplane:
    # 主轮廓本身已包含扇形外缘上的齿形信息。
    body = extrude_profile("XZ", OUTER_PROFILE, THICKNESS)
    # 功能孔位改用解析圆重建，便于后续 CAD 编辑和导出。
    body = body.cut(
        cq.Workplane("XZ")
        .center(*CENTER_HOLE_POS)
        .circle(CENTER_HOLE_DIAMETER * 0.5)
        .extrude(THICKNESS * 0.75, both=True)
    )
    body = body.cut(
        cq.Workplane("XZ")
        .center(*SMALL_HOLE_POS)
        .circle(SMALL_HOLE_DIAMETER * 0.5)
        .extrude(THICKNESS * 0.75, both=True)
    )
    body = body.cut(
        cq.Workplane("XZ")
        .center(-10.0, -1.0)
        .circle(1.3)
        .extrude(THICKNESS * 0.75, both=True)
    )
    return body


result = build()
