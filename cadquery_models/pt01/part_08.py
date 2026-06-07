from __future__ import annotations

import cadquery as cq

try:
    from .common import spoked_ring
except ImportError:
    from common import spoked_ring


OUTER_RADIUS = 39.0
INNER_RADIUS = 28.0
THICKNESS = 18.0
TOOTH_COUNT = 72
TOOTH_HEIGHT = 3.0
TOOTH_WIDTH = 1.6
RIB_COUNT = 6
RIB_WIDTH = 5.5
HUB_RADIUS = 8.8
HUB_BORE = 5.0
HUB_HOLE_DIAMETER = 4.2
HUB_HOLE_RADIUS = 7.3


def build() -> cq.Workplane:
    body = spoked_ring(
        plane="XY",
        outer_radius=OUTER_RADIUS,
        inner_radius=INNER_RADIUS,
        thickness=THICKNESS,
        tooth_count=TOOTH_COUNT,
        tooth_height=TOOTH_HEIGHT,
        tooth_width=TOOTH_WIDTH,
        rib_count=RIB_COUNT,
        rib_width=RIB_WIDTH,
        hub_radius=HUB_RADIUS,
    )
    body = body.cut(cq.Workplane("XY").circle(HUB_BORE * 0.5).extrude(THICKNESS * 2.0, both=True))
    bolt_holes = (
        cq.Workplane("XY")
        .pushPoints(
            [
                (0, HUB_HOLE_RADIUS),
                (HUB_HOLE_RADIUS, 0),
                (0, -HUB_HOLE_RADIUS),
                (-HUB_HOLE_RADIUS, 0),
            ]
        )
        .circle(HUB_HOLE_DIAMETER * 0.5)
        .extrude(THICKNESS * 2.0, both=True)
    )
    return body.cut(bolt_holes)


result = build()
