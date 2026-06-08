from __future__ import annotations

"""零件 09：带中心通孔和偏心凹腔的小外齿轮。"""

import cadquery as cq

try:
    from .common import extrude_profile, load_profile_points
except ImportError:
    from common import extrude_profile, load_profile_points


# 外轮廓通过高密度二维截面数据保留 STL 的齿形特征。
OUTER_PROFILE = load_profile_points(9)

THICKNESS = 9.0
BORE_DIAMETER = 4.3
POCKET_DIAMETER = 14.0
POCKET_DEPTH = 6.0


def build() -> cq.Workplane:
    # 先拉伸实测齿形轮廓，再补上内部解析孔和凹腔特征。
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
