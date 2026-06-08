from __future__ import annotations

"""零件 10：带槽阵列、侧腿、侧孔和中间加强筋的框形支架。"""

import cadquery as cq


SIZE_X = 50.0
SIZE_Y = 49.938
HEIGHT = 23.0
TOP_THICKNESS = 3.0
LEG_WIDTH = 5.0
TOP_Z_MIN = 4.766
BOTTOM_Z = -15.234

SLOT_POS = [
    (-0.961, 67.961), (-0.961, 87.961), (15.626, 67.954), (-0.703, 77.731),
    (15.379, 77.859), (-0.988, 97.904), (15.447, 97.745), (15.447, 87.745),
]
SMALL_HOLE_POS = [(-20.217, 77.760), (-20.167, 67.893), (-20.121, 87.745)]


def build() -> cq.Workplane:
    center_y = (57.037 + 106.975) * 0.5
    # 顶板上布置矩形槽阵列和几个小圆孔。
    top = (
        cq.Workplane("XY")
        .center(0, center_y)
        .rect(SIZE_X, SIZE_Y)
        .extrude(TOP_THICKNESS)
        .translate((0, 0, TOP_Z_MIN))
    )
    for x, y in SLOT_POS:
        top = top.cut(cq.Workplane("XY").center(x, y).slot2D(14.0, 8.0, 0).extrude(TOP_THICKNESS + 1.0).translate((0, 0, TOP_Z_MIN - 0.5)))
    for x, y in SMALL_HOLE_POS:
        top = top.cut(cq.Workplane("XY").center(x, y).circle(2.65).extrude(TOP_THICKNESS + 1.0).translate((0, 0, TOP_Z_MIN - 0.5)))
    # 两侧立板定义顶板下方的支架主体。
    leg_height = TOP_Z_MIN - BOTTOM_Z
    left_leg = cq.Workplane("XY").center(-22.5 + LEG_WIDTH * 0.5, center_y).rect(LEG_WIDTH, SIZE_Y).extrude(leg_height).translate((0, 0, BOTTOM_Z))
    right_leg = cq.Workplane("XY").center(22.5 - LEG_WIDTH * 0.5, center_y).rect(LEG_WIDTH, SIZE_Y).extrude(leg_height).translate((0, 0, BOTTOM_Z))
    # 侧面圆孔和内部三角筋用于逼近 STL 中可见的支撑细节。
    side_hole = cq.Workplane("XZ").center(0, -4.5).circle(7.0).extrude(LEG_WIDTH * 1.2, both=True)
    left_leg = left_leg.cut(side_hole.translate((-22.5 + LEG_WIDTH * 0.5, 0, 0)))
    right_leg = right_leg.cut(side_hole.translate((22.5 - LEG_WIDTH * 0.5, 0, 0)))
    rib = (
        cq.Workplane("XZ")
        .polyline([(-22.0, -15.0), (22.0, -15.0), (0.0, 4.7)])
        .close()
        .extrude(3.0, both=True)
        .translate((0, center_y, 0.0))
    )
    return top.union(left_leg).union(right_leg).union(rib)


result = build()
