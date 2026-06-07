from __future__ import annotations

import cadquery as cq

try:
    from .common import tooth_tabs
except ImportError:
    from common import tooth_tabs


THICKNESS = 2.7
OUTER_RADIUS = 31.0
INNER_RADIUS = 9.0
SWEEP_DEGREES = 128.0
TOOTH_COUNT = 26
TOOTH_HEIGHT = 3.0
TOOTH_WIDTH = 2.6
LARGE_HOLE_DIAMETER = 10.5
SMALL_HOLE_DIAMETER = 4.0


def build() -> cq.Workplane:
    base = (
        cq.Workplane("XZ")
        .moveTo(0, 0)
        .radiusArc((OUTER_RADIUS * 0.79, OUTER_RADIUS * 0.61), OUTER_RADIUS)
        .radiusArc((OUTER_RADIUS, 0), OUTER_RADIUS * 0.55)
        .lineTo(0, -OUTER_RADIUS * 0.72)
        .close()
        .extrude(THICKNESS * 0.5, both=True)
    )
    base = base.union(
        cq.Workplane("XZ")
        .circle(INNER_RADIUS)
        .extrude(THICKNESS * 0.5, both=True)
        .translate((0, 0, -OUTER_RADIUS * 0.2))
    )
    base = base.cut(
        cq.Workplane("XZ")
        .ellipse(LARGE_HOLE_DIAMETER * 0.6, LARGE_HOLE_DIAMETER * 0.42)
        .extrude(THICKNESS, both=True)
        .translate((0, 0, -3.0))
    )
    for point in [(-17.0, -1.0), (17.0, -1.0), (0.0, -20.0)]:
        base = base.cut(
            cq.Workplane("XZ")
            .center(*point)
            .circle(SMALL_HOLE_DIAMETER * 0.5)
            .extrude(THICKNESS, both=True)
        )
    teeth = tooth_tabs(
        plane="XZ",
        count=TOOTH_COUNT,
        radius=OUTER_RADIUS - TOOTH_HEIGHT * 0.8,
        radial_depth=TOOTH_HEIGHT,
        tangential_width=TOOTH_WIDTH,
        thickness=THICKNESS,
        start_angle=205.0,
    )
    for tooth in teeth:
        center = tooth.val().Center()
        angle = (cq.Vector(center.x, 0, center.z).getSignedAngle(cq.Vector(1, 0, 0)) * 180.0 / 3.141592653589793)
        normalized = (angle + 360.0) % 360.0
        if 140.0 <= normalized <= 320.0:
            base = base.union(tooth)
    rib = (
        cq.Workplane("YZ")
        .polyline([(0, 0), (THICKNESS, 0), (0, 18.0)])
        .close()
        .extrude(8.0, both=True)
        .translate((0, 0, -8.0))
    )
    return base.union(rib)


result = build()
