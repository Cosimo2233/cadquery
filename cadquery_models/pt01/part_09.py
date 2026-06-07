from __future__ import annotations

import cadquery as cq

try:
    from .common import extrude_profile, load_profile_points
except ImportError:
    from common import extrude_profile, load_profile_points


OUTER_PROFILE = load_profile_points(9)

THICKNESS = 9.0
BORE_DIAMETER = 4.3
POCKET_DIAMETER = 14.0
POCKET_DEPTH = 6.0


def build() -> cq.Workplane:
    body = extrude_profile("XY", OUTER_PROFILE, THICKNESS)
    body = body.cut(cq.Workplane("XY").circle(BORE_DIAMETER * 0.5).extrude(THICKNESS * 0.75, both=True))
    pocket = (
        cq.Workplane("XY")
        .circle(POCKET_DIAMETER * 0.5)
        .extrude(POCKET_DEPTH)
        .translate((0, 51.4, THICKNESS * 0.5 - POCKET_DEPTH))
    )
    return body.cut(pocket)


result = build()
