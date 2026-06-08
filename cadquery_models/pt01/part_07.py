from __future__ import annotations

"""零件 07：短圆柱销。"""

import cadquery as cq


DIAMETER = 7.95
LENGTH = 40.0


def build() -> cq.Workplane:
    # 直接用解析圆柱表示，匹配测得的直径和长度。
    return cq.Workplane("XY").circle(DIAMETER * 0.5).extrude(LENGTH * 0.5, both=True)


result = build()
