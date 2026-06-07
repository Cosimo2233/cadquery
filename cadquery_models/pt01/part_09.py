from __future__ import annotations

import cadquery as cq

try:
    from .common import simple_gear
except ImportError:
    from common import simple_gear


ROOT_RADIUS = 9.1
TOOTH_HEIGHT = 2.8
TOOTH_WIDTH = 3.0
TOOTH_COUNT = 16
THICKNESS = 9.0
BORE_DIAMETER = 6.8
TOP_RING_DIAMETER = 13.0
TOP_RING_HEIGHT = 3.0


def build() -> cq.Workplane:
    gear = simple_gear(
        plane="XY",
        root_radius=ROOT_RADIUS,
        tooth_count=TOOTH_COUNT,
        tooth_height=TOOTH_HEIGHT,
        tooth_width=TOOTH_WIDTH,
        thickness=THICKNESS,
        bore_diameter=BORE_DIAMETER,
    )
    ring = (
        cq.Workplane("XY")
        .circle(TOP_RING_DIAMETER * 0.5)
        .circle(BORE_DIAMETER * 0.5)
        .extrude(TOP_RING_HEIGHT)
        .translate((0, 0, THICKNESS * 0.5 - TOP_RING_HEIGHT))
    )
    return gear.union(ring)


result = build()
