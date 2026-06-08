from __future__ import annotations

"""零件 05：带通孔和浅沉孔的小齿轮。"""

import cadquery as cq

try:
    from .common import extrude_profile, load_profile_points
except ImportError:
    from common import extrude_profile, load_profile_points


# 高密度外轮廓尽量保留原 STL 中截面的齿形细节。
OUTER_PROFILE = load_profile_points(5)

LENGTH = 22.0
BORE_DIAMETER = 4.3
COUNTERBORE_DIAMETER = 14.0
COUNTERBORE_DEPTH = 2.0


def build() -> cq.Workplane:
    # 通过拉伸中截面轮廓来保留齿轮外缘的真实齿形。
    body = extrude_profile("XZ", OUTER_PROFILE, LENGTH)
    # 中心通孔和两侧沉孔保持为解析几何，便于制造和后续编辑。
    body = body.cut(cq.Workplane("XZ").circle(BORE_DIAMETER * 0.5).extrude(LENGTH * 0.75, both=True).translate((0, 0, -41.8)))
    top_counterbore = (
        cq.Workplane("XZ")
        .circle(COUNTERBORE_DIAMETER * 0.5)
        .extrude(COUNTERBORE_DEPTH)
        .translate((0, 0, -41.8 - LENGTH * 0.5))
    )
    bottom_counterbore = (
        cq.Workplane("XZ")
        .circle(COUNTERBORE_DIAMETER * 0.5)
        .extrude(COUNTERBORE_DEPTH)
        .translate((0, LENGTH - COUNTERBORE_DEPTH, -41.8 - LENGTH * 0.5))
    )
    return body.cut(top_counterbore).cut(bottom_counterbore)


result = build()
