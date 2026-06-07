from __future__ import annotations

import cadquery as cq

try:
    from .common import extrude_profile, load_profile_points
except ImportError:
    from common import extrude_profile, load_profile_points


OUTER_PROFILE = load_profile_points(8)

THICKNESS = 18.0
CENTER_HOLE_DIAMETER = 30.0
CENTER_RECESS_DEPTH = 16.0
BOLT_HOLE_DIAMETER = 3.4
BOLT_HOLE_RADIUS = 10.0


def build() -> cq.Workplane:
    body = extrude_profile("XY", OUTER_PROFILE, THICKNESS)
    center_recess = (
        cq.Workplane("XY")
        .circle(CENTER_HOLE_DIAMETER * 0.5)
        .extrude(CENTER_RECESS_DEPTH)
        .translate((0, 0, THICKNESS * 0.5 - CENTER_RECESS_DEPTH))
    )
    body = body.cut(center_recess)
    bolt_holes = (
        cq.Workplane("XY")
        .pushPoints([(0, BOLT_HOLE_RADIUS), (BOLT_HOLE_RADIUS, 0), (0, -BOLT_HOLE_RADIUS), (-BOLT_HOLE_RADIUS, 0)])
        .circle(BOLT_HOLE_DIAMETER * 0.5)
        .extrude(THICKNESS * 0.6)
        .translate((0, 0, -THICKNESS * 0.5))
    )
    hub = (
        cq.Workplane("XY")
        .circle(11.8)
        .extrude(2.0)
        .translate((0, 0, -THICKNESS * 0.5))
    )
    return body.union(hub).cut(bolt_holes)


result = build()
