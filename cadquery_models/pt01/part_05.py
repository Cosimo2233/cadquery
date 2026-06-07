from __future__ import annotations

import cadquery as cq

try:
    from .common import simple_gear
except ImportError:
    from common import simple_gear


ROOT_RADIUS = 8.2
TOOTH_HEIGHT = 3.4
TOOTH_WIDTH = 4.0
TOOTH_COUNT = 14
LENGTH = 22.0
BORE_DIAMETER = 7.2
RIB_COUNT = 8
RIB_DEPTH = 1.8
RIB_WIDTH = 4.8


def build() -> cq.Workplane:
    body = simple_gear(
        plane="XZ",
        root_radius=ROOT_RADIUS,
        tooth_count=TOOTH_COUNT,
        tooth_height=TOOTH_HEIGHT,
        tooth_width=TOOTH_WIDTH,
        thickness=LENGTH,
        bore_diameter=BORE_DIAMETER,
        start_angle=360.0 / TOOTH_COUNT * 0.5,
    )
    for angle in range(RIB_COUNT):
        rib = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, 360.0 * angle / RIB_COUNT))
            .center(ROOT_RADIUS - 0.8, 0)
            .rect(2.2, RIB_WIDTH)
            .extrude(LENGTH * 0.36, both=True)
        )
        body = body.cut(rib)
    return body


result = build()
