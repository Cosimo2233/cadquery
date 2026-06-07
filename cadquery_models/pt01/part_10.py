from __future__ import annotations

import cadquery as cq


SIZE_X = 50.0
SIZE_Y = 49.938
HEIGHT = 23.0
TOP_THICKNESS = 4.0
LEG_THICKNESS = 5.0


def build() -> cq.Workplane:
    top = (
        cq.Workplane("XY")
        .rect(SIZE_X, SIZE_Y)
        .extrude(TOP_THICKNESS * 0.5, both=True)
        .translate((0, 0, HEIGHT * 0.5 - TOP_THICKNESS * 0.5))
    )
    left_x = -17.0
    for y in [12.0, 0.0, -12.0]:
        top = top.cut(cq.Workplane("XY").center(left_x, y).circle(4.2).extrude(TOP_THICKNESS * 2.5, both=True))
    for x in [2.0, 17.0]:
        for y in [12.0, 0.0, -12.0]:
            top = top.cut(cq.Workplane("XY").center(x, y).slot2D(12.0, 8.0, 0).extrude(TOP_THICKNESS * 2.5, both=True))
    leg = (
        cq.Workplane("XY")
        .center(-SIZE_X * 0.5 + LEG_THICKNESS * 0.5, 0)
        .rect(LEG_THICKNESS, SIZE_Y * 0.88)
        .extrude(HEIGHT - TOP_THICKNESS)
        .translate((0, 0, HEIGHT * 0.5 - TOP_THICKNESS - (HEIGHT - TOP_THICKNESS)))
    )
    legs = leg.union(leg.mirror("YZ"))
    side_opening = (
        cq.Workplane("XZ")
        .center(0, -2.0)
        .circle(8.0)
        .extrude(LEG_THICKNESS * 2.2, both=True)
        .translate((0, 0, -4.0))
    )
    legs = legs.cut(side_opening.translate((-(SIZE_X * 0.5 - LEG_THICKNESS * 0.5), 0, 0)))
    legs = legs.cut(side_opening.translate(((SIZE_X * 0.5 - LEG_THICKNESS * 0.5), 0, 0)))
    center_hole = (
        cq.Workplane("XZ")
        .center(0, -3.0)
        .circle(7.0)
        .extrude(SIZE_Y * 0.42, both=True)
    )
    rib = (
        cq.Workplane("XZ")
        .polyline([(-SIZE_X * 0.36, 0), (SIZE_X * 0.36, 0), (0, -HEIGHT * 0.42)])
        .close()
        .extrude(3.0, both=True)
        .translate((0, 0, 2.5))
    )
    return top.union(legs).union(rib).cut(center_hole)


result = build()
