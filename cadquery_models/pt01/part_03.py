from __future__ import annotations

"""零件 03：带大孔、顶部小孔和底部加厚边的板式支架。"""

import cadquery as cq

try:
    from .common import extrude_profile
except ImportError:
    from common import extrude_profile


FRONT_PROFILE = [
    (-22.500, -62.200),
    (22.500, -62.200),
    (22.496, 3.293),
    (20.572, 9.944),
    (17.112, 12.194),
    (-17.510, 12.147),
    (-21.002, 9.257),
    (-22.500, 2.963),
]

THICKNESS = 20.468
MAIN_HOLE_DIAMETER = 28.0
MAIN_HOLE_POS = (0.177, -40.303)
TOP_HOLE_DIAMETER = 8.2
TOP_HOLE_POS = (0.0, -0.286)
CORNER_HOLE_DIAMETER = 3.2
CORNER_HOLE_POS = [(-15.365, -55.543), (15.573, -55.543), (-15.351, -24.597), (15.559, -24.597)]
BASE_WIDTH = 45.0
BASE_HEIGHT = 3.0
BASE_Z = -60.7
Y_MID = -38.811


def build() -> cq.Workplane:
    # 正视轮廓用于还原支架顶部两侧的圆滑肩部外形。
    body = extrude_profile("XZ", FRONT_PROFILE, THICKNESS).translate((0, Y_MID, 0))
    # 主安装孔和辅助孔统一用解析圆孔切除。
    body = body.cut(
        cq.Workplane("XZ")
        .center(*MAIN_HOLE_POS)
        .circle(MAIN_HOLE_DIAMETER * 0.5)
        .extrude(THICKNESS * 0.75, both=True)
        .translate((0, Y_MID, 0))
    )
    body = body.cut(
        cq.Workplane("XZ")
        .center(*TOP_HOLE_POS)
        .circle(TOP_HOLE_DIAMETER * 0.5)
        .extrude(THICKNESS * 0.75, both=True)
        .translate((0, Y_MID, 0))
    )
    corner_cutters = (
        cq.Workplane("XZ")
        .pushPoints(CORNER_HOLE_POS)
        .circle(CORNER_HOLE_DIAMETER * 0.5)
        .extrude(THICKNESS * 0.75, both=True)
        .translate((0, Y_MID, 0))
    )
    body = body.cut(corner_cutters)
    # 底边额外加一条矩形基座，用来逼近 STL 的下缘加强区。
    base = (
        cq.Workplane("XZ")
        .center(0, BASE_Z)
        .rect(BASE_WIDTH, BASE_HEIGHT)
        .extrude(THICKNESS * 0.5, both=True)
        .translate((0, Y_MID, 0))
    )
    return body.union(base)


result = build()
