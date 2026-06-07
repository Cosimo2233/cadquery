from __future__ import annotations

import cadquery as cq


BODY_WIDTH = 45.0
BODY_LENGTH = 150.0
THICKNESS = 4.0
BIG_HOLE_DIAMETER = 18.0
SLOT_LENGTH = 18.0
SLOT_DIAMETER = 10.0
HUB_RADIUS = 12.0
HUB_HEIGHT = 6.5
SMALL_HOLE_DIAMETER = 4.2


def build() -> cq.Workplane:
    plate = cq.Workplane("XY").rect(BODY_WIDTH, BODY_LENGTH).extrude(THICKNESS, both=True)
    plate = plate.edges("|Z").fillet(2.0)
    plate = plate.cut(
        cq.Workplane("XY")
        .center(0, BODY_LENGTH * 0.33)
        .circle(BIG_HOLE_DIAMETER * 0.5)
        .extrude(THICKNESS * 2.5, both=True)
    )
    plate = plate.cut(
        cq.Workplane("XY")
        .center(0, -BODY_LENGTH * 0.28)
        .slot2D(SLOT_LENGTH, SLOT_DIAMETER, 0)
        .extrude(THICKNESS * 2.5, both=True)
    )
    for point in [(-15.0, 55.0), (15.0, 55.0), (-12.0, -42.0), (12.0, -42.0)]:
        plate = plate.cut(
            cq.Workplane("XY")
            .center(point[0], point[1])
            .circle(SMALL_HOLE_DIAMETER * 0.5)
            .extrude(THICKNESS * 2.5, both=True)
        )
    hub = (
        cq.Workplane("XY")
        .circle(HUB_RADIUS)
        .extrude(HUB_HEIGHT)
        .translate((0, 5.0, -THICKNESS * 0.5 - HUB_HEIGHT + 1.5))
    )
    hub = hub.cut(
        cq.Workplane("XY")
        .circle(4.2)
        .extrude(HUB_HEIGHT * 2.0, both=True)
        .translate((0, 5.0, -THICKNESS * 0.5 - HUB_HEIGHT * 0.5 + 1.5))
    )
    web = (
        cq.Workplane("YZ")
        .polyline([(0, 0), (0, 9.0), (30.0, 0)])
        .close()
        .extrude(BODY_WIDTH * 0.42, both=True)
        .translate((0, -5.0, -THICKNESS * 0.5))
    )
    return plate.union(hub).union(web)


result = build()
