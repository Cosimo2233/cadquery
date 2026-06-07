from __future__ import annotations

import cadquery as cq


SIZE = 50.0
HEIGHT = 22.0
TOP_THICKNESS = 4.0
LEG_WIDTH = 5.0
TOP_Z_MIN = 3.743
BOTTOM_Z = -14.257


def build() -> cq.Workplane:
    top = (
        cq.Workplane("XY")
        .rect(SIZE, SIZE)
        .extrude(TOP_THICKNESS)
        .translate((0, -7.56, TOP_Z_MIN))
    )
    for y in [7.924, -7.454, -23.151]:
        top = top.cut(
            cq.Workplane("XY")
            .center(12.0, y)
            .slot2D(18.0, 4.0, 0)
            .extrude(TOP_THICKNESS + 1.0)
            .translate((0, 0, TOP_Z_MIN - 0.5))
        )
    top = top.cut(cq.Workplane("XY").center(-14.0, -15.0).circle(3.1).extrude(TOP_THICKNESS + 1.0).translate((0, 0, TOP_Z_MIN - 0.5)))
    top = top.cut(cq.Workplane("XY").center(-14.0, 0.0).circle(3.1).extrude(TOP_THICKNESS + 1.0).translate((0, 0, TOP_Z_MIN - 0.5)))
    bridge_cut = cq.Workplane("XY").center(-6.027, -8.045).rect(6.0, 40.0).extrude(TOP_THICKNESS + 1.0).translate((0, 0, TOP_Z_MIN - 0.5))
    top = top.cut(bridge_cut)
    leg_height = TOP_Z_MIN - BOTTOM_Z
    left_leg = cq.Workplane("XY").center(-22.5 + LEG_WIDTH * 0.5, -7.56).rect(LEG_WIDTH, 50.0).extrude(leg_height).translate((0, 0, BOTTOM_Z))
    right_leg = cq.Workplane("XY").center(22.5 - LEG_WIDTH * 0.5, -7.56).rect(LEG_WIDTH, 50.0).extrude(leg_height).translate((0, 0, BOTTOM_Z))
    rib = (
        cq.Workplane("XZ")
        .polyline([(-22.0, -12.8), (22.0, -12.8), (0.0, 3.8)])
        .close()
        .extrude(3.0, both=True)
        .translate((0, -7.56, 0.0))
    )
    return top.union(left_leg).union(right_leg).union(rib)


result = build()
