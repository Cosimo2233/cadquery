from __future__ import annotations

import cadquery as cq

from .common import corner_holes


FRAME_WIDTH = 45.0
FRAME_HEIGHT = 74.4
PLATE_THICKNESS = 4.0
BASE_DEPTH = 16.4
BASE_THICKNESS = 6.0
LARGE_HOLE_DIAMETER = 22.0
SMALL_HOLE_DIAMETER = 4.0


def build() -> cq.Workplane:
    plate = (
        cq.Workplane("XZ")
        .rect(FRAME_WIDTH, FRAME_HEIGHT)
        .extrude(PLATE_THICKNESS)
        .translate((0, 0, -9.0))
    )
    plate = plate.cut(
        cq.Workplane("XZ")
        .ellipse(LARGE_HOLE_DIAMETER * 0.6, LARGE_HOLE_DIAMETER * 0.45)
        .extrude(PLATE_THICKNESS * 2.0, both=True)
        .translate((0, 0, -11.0))
    )
    plate = corner_holes(
        body=plate,
        plane="XZ",
        width=FRAME_WIDTH,
        height=FRAME_HEIGHT,
        offset_x=4.5,
        offset_y=4.5,
        diameter=SMALL_HOLE_DIAMETER,
        depth=PLATE_THICKNESS * 2.0,
    )
    base = (
        cq.Workplane("XY")
        .rect(FRAME_WIDTH, BASE_DEPTH)
        .extrude(BASE_THICKNESS)
        .translate((0, BASE_DEPTH * 0.5, -FRAME_HEIGHT * 0.5 - BASE_THICKNESS * 0.5 + 4.0))
    )
    rail_span = 12.0
    rails = (
        cq.Workplane("XY")
        .pushPoints([(0, rail_span * 0.5), (0, -rail_span * 0.5)])
        .rect(FRAME_WIDTH * 0.86, 3.0)
        .extrude(3.0)
        .translate((0, BASE_DEPTH * 0.5, -FRAME_HEIGHT * 0.5 + 2.5))
    )
    left_rib = (
        cq.Workplane("YZ")
        .polyline([(0, -2.0), (0, 2.0), (16.0, 0)])
        .close()
        .extrude(PLATE_THICKNESS)
        .translate((-FRAME_WIDTH * 0.5 + PLATE_THICKNESS * 0.5, BASE_DEPTH * 0.22, -FRAME_HEIGHT * 0.5 + 7.0))
    )
    right_rib = left_rib.mirror("YZ")
    return plate.union(base).union(rails).union(left_rib).union(right_rib)


result = build()
