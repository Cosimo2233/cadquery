from __future__ import annotations

import cadquery as cq


SIZE = 50.0
HEIGHT = 22.0
TOP_THICKNESS = 4.0
LEG_THICKNESS = 5.0
LEG_DEPTH = HEIGHT - TOP_THICKNESS


def build() -> cq.Workplane:
    top = (
        cq.Workplane("XY")
        .rect(SIZE, SIZE)
        .extrude(TOP_THICKNESS * 0.5, both=True)
        .translate((0, 0, HEIGHT * 0.5 - TOP_THICKNESS * 0.5))
    )
    for x, y, length, diameter in [
        (-11.0, 4.0, 18.0, 8.0),
        (9.0, 12.0, 16.0, 7.0),
        (10.0, 0.0, 16.0, 7.0),
        (10.0, -12.0, 16.0, 7.0),
    ]:
        top = top.cut(cq.Workplane("XY").center(x, y).slot2D(length, diameter, 90 if x < 0 else 0).extrude(TOP_THICKNESS * 2.5, both=True))
    legs = cq.Workplane("XY")
    for x in [-SIZE * 0.5 + LEG_THICKNESS * 0.5, SIZE * 0.5 - LEG_THICKNESS * 0.5]:
        legs = legs.union(
            cq.Workplane("XY")
            .center(x, 0)
            .rect(LEG_THICKNESS, SIZE * 0.88)
            .extrude(LEG_DEPTH)
            .translate((0, 0, HEIGHT * 0.5 - TOP_THICKNESS - LEG_DEPTH))
        )
    front_rib = (
        cq.Workplane("XZ")
        .polyline([(-SIZE * 0.4, 0), (SIZE * 0.4, 0), (0, -LEG_DEPTH * 0.45)])
        .close()
        .extrude(3.0, both=True)
        .translate((0, -SIZE * 0.18, 3.0))
    )
    back_rib = front_rib.translate((0, SIZE * 0.36, 0))
    return top.union(legs).union(front_rib).union(back_rib)


result = build()
