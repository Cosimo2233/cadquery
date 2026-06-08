from __future__ import annotations

"""渐开线直齿轮通用建模工具。"""

import math
from dataclasses import dataclass

import cadquery as cq

try:
    from .common import extrude_profile, polar_to_cartesian, sample_circular_arc
except ImportError:
    from common import extrude_profile, polar_to_cartesian, sample_circular_arc


@dataclass(frozen=True)
class SpurGearSpec:
    """直齿轮参数定义。"""

    module: float
    tooth_count: int
    thickness: float
    pressure_angle_deg: float = 20.0
    addendum_coefficient: float = 1.0
    dedendum_coefficient: float = 1.25
    addendum_diameter: float | None = None
    dedendum_diameter: float | None = None
    bore_diameter: float | None = None
    backlash: float = 0.0

    @property
    def pressure_angle_rad(self) -> float:
        return math.radians(self.pressure_angle_deg)

    @property
    def pitch_diameter(self) -> float:
        return self.module * self.tooth_count

    @property
    def pitch_radius(self) -> float:
        return self.pitch_diameter * 0.5

    @property
    def circular_pitch(self) -> float:
        return math.pi * self.module

    @property
    def base_radius(self) -> float:
        return self.pitch_radius * math.cos(self.pressure_angle_rad)

    @property
    def addendum_radius(self) -> float:
        if self.addendum_diameter is not None:
            return self.addendum_diameter * 0.5
        return self.pitch_radius + self.module * self.addendum_coefficient

    @property
    def dedendum_radius(self) -> float:
        if self.dedendum_diameter is not None:
            return self.dedendum_diameter * 0.5
        return max(0.05, self.pitch_radius - self.module * self.dedendum_coefficient)

    @property
    def base_diameter(self) -> float:
        return self.base_radius * 2.0

    @property
    def addendum_circle_diameter(self) -> float:
        return self.addendum_radius * 2.0

    @property
    def dedendum_circle_diameter(self) -> float:
        return self.dedendum_radius * 2.0

    @property
    def tooth_pitch_angle(self) -> float:
        return 2.0 * math.pi / self.tooth_count

    def summary(self) -> dict[str, float]:
        """返回常用齿轮参数，便于调试和复核。"""
        return {
            "module": self.module,
            "tooth_count": float(self.tooth_count),
            "pressure_angle_deg": self.pressure_angle_deg,
            "pitch_diameter": self.pitch_diameter,
            "base_diameter": self.base_diameter,
            "addendum_circle_diameter": self.addendum_circle_diameter,
            "dedendum_circle_diameter": self.dedendum_circle_diameter,
            "thickness": self.thickness,
        }


def _involute_function(t: float) -> float:
    return t - math.atan(t)


def involute_point(base_radius: float, t: float) -> tuple[float, float]:
    """返回基圆上参数为 t 的渐开线点。"""
    x = base_radius * (math.cos(t) + t * math.sin(t))
    y = base_radius * (math.sin(t) - t * math.cos(t))
    return x, y


def involute_parameter_for_radius(base_radius: float, radius: float) -> float:
    """由目标半径反求渐开线参数 t。"""
    if radius < base_radius:
        raise ValueError("radius must be greater than or equal to base_radius")
    return math.sqrt((radius / base_radius) ** 2 - 1.0)


def involute_polar_angle(base_radius: float, radius: float) -> float:
    """返回渐开线点相对于基圆切点的极角增量。"""
    return _involute_function(involute_parameter_for_radius(base_radius, radius))


def involute_curve_points(
    base_radius: float,
    start_radius: float,
    end_radius: float,
    samples: int,
    rotation_rad: float = 0.0,
) -> list[tuple[float, float]]:
    """采样一段渐开线。"""
    if end_radius < start_radius:
        raise ValueError("end_radius must be greater than or equal to start_radius")
    if start_radius < base_radius:
        raise ValueError("start_radius must be greater than or equal to base_radius")
    if samples < 2:
        raise ValueError("samples must be at least 2")

    start_t = involute_parameter_for_radius(base_radius, start_radius)
    end_t = involute_parameter_for_radius(base_radius, end_radius)
    points: list[tuple[float, float]] = []
    for i in range(samples):
        t = start_t + (end_t - start_t) * i / (samples - 1)
        x, y = involute_point(base_radius, t)
        cos_r = math.cos(rotation_rad)
        sin_r = math.sin(rotation_rad)
        points.append((x * cos_r - y * sin_r, x * sin_r + y * cos_r))
    return points


def _dedupe_points(points: list[tuple[float, float]], tolerance: float = 1e-6) -> list[tuple[float, float]]:
    deduped: list[tuple[float, float]] = []
    for x, y in points:
        if not deduped:
            deduped.append((x, y))
            continue
        px, py = deduped[-1]
        if math.hypot(x - px, y - py) > tolerance:
            deduped.append((x, y))
    if len(deduped) > 1:
        x0, y0 = deduped[0]
        x1, y1 = deduped[-1]
        if math.hypot(x0 - x1, y0 - y1) <= tolerance:
            deduped.pop()
    return deduped


def build_spur_gear_outline(
    spec: SpurGearSpec,
    involute_samples: int = 12,
    root_arc_samples: int = 6,
    tip_arc_samples: int = 6,
) -> list[tuple[float, float]]:
    """构造整圈渐开线直齿轮的二维外轮廓。"""
    if spec.tooth_count < 3:
        raise ValueError("tooth_count must be at least 3")
    if spec.module <= 0:
        raise ValueError("module must be positive")
    if spec.thickness <= 0:
        raise ValueError("thickness must be positive")
    if spec.addendum_radius <= spec.pitch_radius:
        raise ValueError("addendum circle must be outside the pitch circle")
    if spec.dedendum_radius >= spec.pitch_radius:
        raise ValueError("dedendum circle must be inside the pitch circle")

    pitch_half_angle = (math.pi / (2.0 * spec.tooth_count)) - (spec.backlash / (2.0 * spec.pitch_radius))
    if pitch_half_angle <= 0:
        raise ValueError("backlash is too large for the given gear")

    pitch_involute_angle = involute_polar_angle(spec.base_radius, spec.pitch_radius)
    flank_rotation = pitch_half_angle - pitch_involute_angle

    top_involute_angle = flank_rotation + involute_polar_angle(spec.base_radius, spec.addendum_radius)

    if spec.dedendum_radius >= spec.base_radius:
        involute_start_radius = spec.dedendum_radius
        involute_start_angle = flank_rotation + involute_polar_angle(spec.base_radius, involute_start_radius)
        needs_root_connector = False
    else:
        involute_start_radius = spec.base_radius
        involute_start_angle = flank_rotation
        needs_root_connector = True

    upper_flank = involute_curve_points(
        spec.base_radius,
        involute_start_radius,
        spec.addendum_radius,
        involute_samples,
        rotation_rad=flank_rotation,
    )
    lower_flank = [(x, -y) for x, y in reversed(upper_flank)]

    outline: list[tuple[float, float]] = []
    for tooth_index in range(spec.tooth_count):
        center_angle = tooth_index * spec.tooth_pitch_angle
        next_center_angle = center_angle + spec.tooth_pitch_angle
        upper_root_angle = center_angle + involute_start_angle
        lower_root_angle = center_angle - involute_start_angle
        next_upper_root_angle = next_center_angle + involute_start_angle

        if tooth_index == 0:
            outline.append(polar_to_cartesian(spec.dedendum_radius, upper_root_angle))

        if needs_root_connector:
            outline.append(polar_to_cartesian(spec.base_radius, upper_root_angle))

        cos_c = math.cos(center_angle)
        sin_c = math.sin(center_angle)
        rotated_upper = [(x * cos_c - y * sin_c, x * sin_c + y * cos_c) for x, y in upper_flank]
        outline.extend(rotated_upper[1:] if rotated_upper else [])

        outline.extend(
            sample_circular_arc(
                spec.addendum_radius,
                center_angle + top_involute_angle,
                center_angle - top_involute_angle,
                tip_arc_samples,
                include_start=False,
                include_end=False,
            )
        )

        rotated_lower = [(x * cos_c - y * sin_c, x * sin_c + y * cos_c) for x, y in lower_flank]
        outline.extend(rotated_lower)

        if needs_root_connector:
            outline.append(polar_to_cartesian(spec.dedendum_radius, lower_root_angle))

        outline.extend(
            sample_circular_arc(
                spec.dedendum_radius,
                lower_root_angle,
                next_upper_root_angle,
                root_arc_samples,
                include_start=False,
                include_end=(tooth_index == spec.tooth_count - 1),
            )
        )

    return _dedupe_points(outline)


def build_tooth_outline(
    spec: SpurGearSpec,
    involute_samples: int = 12,
    tip_arc_samples: int = 6,
) -> list[tuple[float, float]]:
    """构造单个齿的闭合轮廓。

    轮廓会使用一条位于齿根圆内部的辅助闭合边封口，
    后续与齿根圆实体并集后，该辅助边会落在实体内部，不影响最终外轮廓。
    """
    if spec.tooth_count < 3:
        raise ValueError("tooth_count must be at least 3")
    if spec.module <= 0:
        raise ValueError("module must be positive")

    pitch_half_angle = (math.pi / (2.0 * spec.tooth_count)) - (spec.backlash / (2.0 * spec.pitch_radius))
    if pitch_half_angle <= 0:
        raise ValueError("backlash is too large for the given gear")

    pitch_involute_angle = involute_polar_angle(spec.base_radius, spec.pitch_radius)
    flank_phase = pitch_half_angle + pitch_involute_angle
    top_involute_angle = flank_phase - involute_polar_angle(spec.base_radius, spec.addendum_radius)

    if spec.dedendum_radius >= spec.base_radius:
        involute_start_radius = spec.dedendum_radius
        involute_start_angle = flank_phase - involute_polar_angle(spec.base_radius, involute_start_radius)
        needs_root_connector = False
    else:
        involute_start_radius = spec.base_radius
        involute_start_angle = flank_phase
        needs_root_connector = True

    upper_root = polar_to_cartesian(spec.dedendum_radius, involute_start_angle)
    lower_root = polar_to_cartesian(spec.dedendum_radius, -involute_start_angle)

    raw_flank = involute_curve_points(
        spec.base_radius,
        involute_start_radius,
        spec.addendum_radius,
        involute_samples,
        rotation_rad=0.0,
    )
    cos_phase = math.cos(flank_phase)
    sin_phase = math.sin(flank_phase)
    upper_flank = [
        (x * cos_phase + y * sin_phase, x * sin_phase - y * cos_phase)
        for x, y in raw_flank
    ]
    lower_flank = [(x, -y) for x, y in reversed(upper_flank)]

    outline: list[tuple[float, float]] = [upper_root]
    if needs_root_connector:
        outline.append(polar_to_cartesian(spec.base_radius, involute_start_angle))

    outline.extend(upper_flank[1:] if upper_flank else [])
    outline.extend(
        sample_circular_arc(
            spec.addendum_radius,
            top_involute_angle,
            -top_involute_angle,
            tip_arc_samples,
            include_start=False,
            include_end=False,
        )
    )
    outline.extend(lower_flank)

    if needs_root_connector:
        outline.append(lower_root)

    return _dedupe_points(outline)


def build_spur_gear(
    spec: SpurGearSpec,
    plane: str = "XY",
    involute_samples: int = 12,
    root_arc_samples: int = 6,
    tip_arc_samples: int = 6,
) -> cq.Workplane:
    """根据参数直接生成三维直齿轮实体。"""
    if spec.thickness <= 0:
        raise ValueError("thickness must be positive")
    if spec.addendum_radius <= spec.pitch_radius:
        raise ValueError("addendum circle must be outside the pitch circle")
    if spec.dedendum_radius >= spec.pitch_radius:
        raise ValueError("dedendum circle must be inside the pitch circle")

    gear = cq.Workplane(plane).circle(spec.dedendum_radius).extrude(spec.thickness * 0.5, both=True)
    tooth_outline = build_tooth_outline(
        spec,
        involute_samples=involute_samples,
        tip_arc_samples=tip_arc_samples,
    )
    tooth = extrude_profile(plane, tooth_outline, spec.thickness)
    for tooth_index in range(spec.tooth_count):
        angle_deg = tooth_index * 360.0 / spec.tooth_count
        gear = gear.union(tooth.rotate((0, 0, 0), (0, 0, 1), angle_deg))

    if spec.bore_diameter and spec.bore_diameter > 0:
        cutter = cq.Workplane(plane).circle(spec.bore_diameter * 0.5)
        gear = gear.cut(cutter.extrude(spec.thickness * 0.75, both=True))
    solid = gear.solids().val()
    return cq.Workplane(plane).newObject([solid])


def build_spur_gear_blank(spec: SpurGearSpec, plane: str = "XY") -> cq.Workplane:
    """生成齿轮毛坯，用于对照渐开线齿形。"""
    blank = cq.Workplane(plane).circle(spec.addendum_radius).extrude(spec.thickness * 0.5, both=True)
    if spec.bore_diameter and spec.bore_diameter > 0:
        blank = blank.cut(cq.Workplane(plane).circle(spec.bore_diameter * 0.5).extrude(spec.thickness * 0.75, both=True))
    return blank
