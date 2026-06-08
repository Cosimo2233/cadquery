from __future__ import annotations

"""零件 06：带中心环形凸台、端部凸台和多组小孔的长条板件。"""

import cadquery as cq

try:
    from .common import extrude_profile
except ImportError:
    from common import extrude_profile


OUTER_PROFILE = [
    (-20.261, 73.163), (-18.138, 75.000), (18.138, 75.000), (19.900, 73.761),
    (21.362, 70.256), (22.495, 61.133), (22.500, -60.461), (21.949, -67.536),
    (20.434, -72.822), (18.138, -75.000), (-18.138, -75.000), (-19.900, -73.761),
    (-21.362, -70.256), (-22.495, -61.133), (-22.500, 60.461), (-21.949, 67.536),
    (-20.434, 72.822),
]

THICKNESS = 13.0
CENTER_RING_OUTER = 30.0
CENTER_RING_INNER = 22.15
END_BOSS_OUTER = 23.0
END_BOSS_INNER = 9.0
END_BOSS_POS = (1.25, 51.2)
SMALL_HOLE_DIAMETER = 3.3
SMALL_HOLE_POS = [
    (-14.21, 66.90), (16.79, 66.89), (-14.21, 35.90), (16.79, 35.90),
    (-18.00, -41.17), (18.00, -41.17), (-18.00, -32.17), (18.00, -32.17),
]


def build() -> cq.Workplane:
    # 先构建长条主板外轮廓。
    body = extrude_profile("XY", OUTER_PROFILE, THICKNESS)
    # 中间环形凸台和端部凸台作为独立功能特征叠加。
    center_ring = cq.Workplane("XY").circle(CENTER_RING_OUTER * 0.5).circle(CENTER_RING_INNER * 0.5).extrude(7.895).translate((0, 0, -THICKNESS * 0.5))
    end_boss = cq.Workplane("XY").center(*END_BOSS_POS).circle(END_BOSS_OUTER * 0.5).circle(END_BOSS_INNER * 0.5).extrude(3.0)
    body = body.union(center_ring).union(end_boss)
    # 小孔在并体后统一切出，保证孔贯穿最终实体。
    small_cuts = cq.Workplane("XY").pushPoints(SMALL_HOLE_POS).circle(SMALL_HOLE_DIAMETER * 0.5).extrude(THICKNESS * 0.75, both=True)
    return body.cut(small_cuts)


result = build()
