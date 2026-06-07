from __future__ import annotations

import cadquery as cq

try:
    from .common import extrude_profile, load_profile_points
except ImportError:
    from common import extrude_profile, load_profile_points


OUTER_PROFILE = load_profile_points(2)

THICKNESS = 4.0
CENTER_HOLE_DIAMETER = 8.5
CENTER_HOLE_POS = (0.225, -0.486)
SMALL_HOLE_DIAMETER = 3.2
SMALL_HOLE_POS = (10.410, -0.180)


def build() -> cq.Workplane:
    body = extrude_profile("XZ", OUTER_PROFILE, THICKNESS)
    body = body.cut(
        cq.Workplane("XZ")
        .center(*CENTER_HOLE_POS)
        .circle(CENTER_HOLE_DIAMETER * 0.5)
        .extrude(THICKNESS * 0.75, both=True)
    )
    body = body.cut(
        cq.Workplane("XZ")
        .center(*SMALL_HOLE_POS)
        .circle(SMALL_HOLE_DIAMETER * 0.5)
        .extrude(THICKNESS * 0.75, both=True)
    )
    body = body.cut(
        cq.Workplane("XZ")
        .center(-10.0, -1.0)
        .circle(1.3)
        .extrude(THICKNESS * 0.75, both=True)
    )
    return body


result = build()
