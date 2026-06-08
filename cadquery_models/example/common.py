from __future__ import annotations

"""渐开线齿轮示例共用的轻量几何工具。"""

import math
from typing import Sequence

import cadquery as cq
import numpy as np


def closed_profile(workplane: cq.Workplane, points: Sequence[tuple[float, float]]) -> cq.Workplane:
    """按给定点列绘制并闭合二维轮廓。"""
    return workplane.polyline(list(points)).close()


def polar_to_cartesian(radius: float, angle_rad: float) -> tuple[float, float]:
    """将极坐标转换为二维笛卡尔坐标。"""
    return radius * math.cos(angle_rad), radius * math.sin(angle_rad)


def sample_circular_arc(
    radius: float,
    start_angle_rad: float,
    end_angle_rad: float,
    point_count: int,
    *,
    include_start: bool = True,
    include_end: bool = True,
) -> list[tuple[float, float]]:
    """在圆弧上均匀采样点。"""
    if point_count < 2:
        raise ValueError("point_count must be at least 2")

    angles = np.linspace(start_angle_rad, end_angle_rad, point_count)
    if not include_start:
        angles = angles[1:]
    if not include_end:
        angles = angles[:-1]
    return [polar_to_cartesian(radius, float(angle)) for angle in angles]


def extrude_profile(
    plane: str,
    outer_points: Sequence[tuple[float, float]],
    thickness: float,
    holes: Sequence[Sequence[tuple[float, float]]] | None = None,
    both: bool = True,
) -> cq.Workplane:
    """将二维外轮廓和可选内孔轮廓拉伸成三维实体。"""
    sketch = closed_profile(cq.Workplane(plane), outer_points)
    for hole in holes or ():
        sketch = closed_profile(sketch, hole)
    distance = thickness * 0.5 if both else thickness
    return sketch.extrude(distance, both=both)
