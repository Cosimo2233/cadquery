from __future__ import annotations

import cadquery as cq


DIAMETER = 7.95
LENGTH = 85.0


def build() -> cq.Workplane:
    return cq.Workplane("XZ").circle(DIAMETER * 0.5).extrude(LENGTH * 0.5, both=True)


result = build()
