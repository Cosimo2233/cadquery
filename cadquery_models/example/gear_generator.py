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
    """直齿轮参数定义。

    该数据类保存用户直接输入的几何参数，并通过一组 property
    推导出分度圆、基圆、齿顶圆、齿根圆等常用量。
    """

    # 模数 m，决定齿轮整体尺度，单位通常为 mm
    module: float
    # 齿数 z，即整圈一共有多少个齿
    tooth_count: int
    # 齿轮厚度 b，即沿拉伸方向的实体厚度
    thickness: float

    # 压力角 alpha，默认 20 度，会影响基圆大小和齿形
    pressure_angle_deg: float = 20.0
    # 齿顶高系数 ha*，默认 1.0；齿顶高 = module * addendum_coefficient
    addendum_coefficient: float = 1.0
    # 齿根高系数 hf*，默认 1.25；齿根高 = module * dedendum_coefficient
    dedendum_coefficient: float = 1.25

    # 齿顶圆直径 da；如果提供，则直接使用该值，不再按模数和齿顶高系数推导
    addendum_diameter: float | None = None
    # 齿根圆直径 df；如果提供，则直接使用该值，不再按模数和齿根高系数推导
    dedendum_diameter: float | None = None

    # 中心孔直径 d_bore；用于生侧xi
    bore_diameter: float | None = None
    # 侧隙 backlash；用于减小分度圆处齿厚，给装配留出间隙
    backlash: float = 0.1
    # 齿轮扇形角度，单位 deg；默认 360 表示完整齿轮，小于 360 时生成扇形齿轮
    sector_angle_deg: float = 360.0

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
            "sector_angle_deg": self.sector_angle_deg,
        }


@dataclass(frozen=True)
class InternalRingGearSpec:
    """内齿圈参数定义。

    内齿圈的齿顶圆位于分度圆内侧，齿根圆位于分度圆外侧。
    `outer_diameter` 定义齿圈实体的外圆直径。
    """

    # 模数 m，需与啮合的太阳轮/行星轮一致
    module: float
    # 内齿圈齿数 z
    tooth_count: int
    # 齿圈厚度 b，即沿拉伸方向的实体厚度
    thickness: float
    # 齿圈实体外圆直径
    outer_diameter: float

    # 压力角 alpha，默认 20 度
    pressure_angle_deg: float = 20.0
    # 内齿齿顶高系数 ha*；齿顶圆位于分度圆内侧
    addendum_coefficient: float = 1.0
    # 内齿齿根高系数 hf*；齿根圆位于分度圆外侧
    dedendum_coefficient: float = 1.25

    # 内齿齿顶圆直径；如果提供，则直接使用该值
    addendum_diameter: float | None = None
    # 内齿齿根圆直径；如果提供，则直接使用该值
    dedendum_diameter: float | None = None

    # 齿槽侧隙；用于增大分度圆处齿槽宽度，给啮合留出间隙
    backlash: float = 0.1
    # 齿圈扇形角度，单位 deg；默认 360 表示完整内齿圈
    sector_angle_deg: float = 360.0

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
        return self.pitch_radius - self.module * self.addendum_coefficient

    @property
    def dedendum_radius(self) -> float:
        if self.dedendum_diameter is not None:
            return self.dedendum_diameter * 0.5
        return self.pitch_radius + self.module * self.dedendum_coefficient

    @property
    def outer_radius(self) -> float:
        return self.outer_diameter * 0.5

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
        """返回常用内齿圈参数，便于调试和复核。"""
        return {
            "module": self.module,
            "tooth_count": float(self.tooth_count),
            "pressure_angle_deg": self.pressure_angle_deg,
            "pitch_diameter": self.pitch_diameter,
            "base_diameter": self.base_diameter,
            "addendum_circle_diameter": self.addendum_circle_diameter,
            "dedendum_circle_diameter": self.dedendum_circle_diameter,
            "outer_diameter": self.outer_diameter,
            "thickness": self.thickness,
            "sector_angle_deg": self.sector_angle_deg,
        }


def _involute_function(t: float) -> float:
    """标准渐开线函数 inv(t) = t - atan(t)。"""
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
    """采样一段渐开线。

    `rotation_rad` 用于将标准位置的渐开线整体旋转到目标角度。
    """
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
    """移除连续重复点，避免轮廓中出现退化短边。"""
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


def validate_spur_gear_spec(spec: SpurGearSpec) -> None:
    """检查齿轮参数是否足以生成完整实体。"""
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
    if spec.sector_angle_deg <= 0 or spec.sector_angle_deg > 360:
        raise ValueError("sector_angle_deg must be greater than 0 and less than or equal to 360")

    if spec.bore_diameter is not None:
        if spec.bore_diameter < 0:
            raise ValueError("中心孔直径 bore_diameter 不能为负数。")
        bore_radius = spec.bore_diameter * 0.5
        if bore_radius >= spec.dedendum_radius:
            raise ValueError(
                "中心孔过大，无法生成完整齿轮实体。\n"
                f"- 当前中心孔直径: {spec.bore_diameter:.3f} mm\n"
                f"- 当前齿根圆直径: {spec.dedendum_circle_diameter:.3f} mm\n"
                f"- 当前分度圆直径: {spec.pitch_diameter:.3f} mm\n"
                f"- 当前齿顶圆直径: {spec.addendum_circle_diameter:.3f} mm\n"
                "要求：中心孔直径必须小于齿根圆直径。"
            )


def validate_internal_ring_gear_spec(spec: InternalRingGearSpec) -> None:
    """检查内齿圈参数是否足以生成完整实体。"""
    if spec.tooth_count < 3:
        raise ValueError("tooth_count must be at least 3")
    if spec.module <= 0:
        raise ValueError("module must be positive")
    if spec.thickness <= 0:
        raise ValueError("thickness must be positive")
    if spec.outer_diameter <= 0:
        raise ValueError("outer_diameter must be positive")
    if spec.backlash < 0:
        raise ValueError("backlash must be greater than or equal to 0")
    if spec.sector_angle_deg <= 0 or spec.sector_angle_deg > 360:
        raise ValueError("sector_angle_deg must be greater than 0 and less than or equal to 360")

    if spec.addendum_radius <= 0:
        raise ValueError("addendum circle must have a positive radius")
    if spec.addendum_radius >= spec.pitch_radius:
        raise ValueError("internal gear addendum circle must be inside the pitch circle")
    if spec.dedendum_radius <= spec.pitch_radius:
        raise ValueError("internal gear dedendum circle must be outside the pitch circle")
    if spec.outer_radius <= spec.dedendum_radius:
        raise ValueError(
            "outer_diameter is too small for the internal ring gear.\n"
            f"- 当前外圆直径: {spec.outer_diameter:.3f} mm\n"
            f"- 当前内齿齿根圆直径: {spec.dedendum_circle_diameter:.3f} mm\n"
            "要求：外圆直径必须大于内齿齿根圆直径。"
        )

    space_half_angle = (math.pi / (2.0 * spec.tooth_count)) + (spec.backlash / (2.0 * spec.pitch_radius))
    if space_half_angle >= spec.tooth_pitch_angle * 0.5:
        raise ValueError("backlash is too large for the given internal ring gear")


def _build_sector_cutter_by_radius(
    *,
    radius: float,
    thickness: float,
    sector_angle_deg: float,
    plane: str,
) -> cq.Workplane:
    """按给定半径构造扇形裁剪实体。"""
    half_angle_rad = math.radians(sector_angle_deg * 0.5)

    if sector_angle_deg >= 360.0 - 1e-9:
        return cq.Workplane(plane).circle(radius).extrude(thickness * 0.75, both=True)

    outline = [(0.0, 0.0), polar_to_cartesian(radius, -half_angle_rad)]
    outline.extend(
        sample_circular_arc(
            radius,
            -half_angle_rad,
            half_angle_rad,
            point_count=max(12, int(sector_angle_deg // 5) + 2),
            include_start=False,
            include_end=True,
        )
    )
    return extrude_profile(plane, outline, thickness * 1.5)


def _build_sector_cutter(spec: SpurGearSpec, plane: str) -> cq.Workplane:
    """构造用于截取扇形齿轮的扇形实体。

    默认将扇形中心放在 +X 方向，并围绕 X 轴两侧对称展开。
    例如 180° 会生成关于 +X 轴对称的半圆齿轮。
    """
    return _build_sector_cutter_by_radius(
        radius=spec.addendum_radius * 1.05,
        thickness=spec.thickness,
        sector_angle_deg=spec.sector_angle_deg,
        plane=plane,
    )


def build_spur_gear_outline(
    spec: SpurGearSpec,
    involute_samples: int = 12,
    root_arc_samples: int = 6,
    tip_arc_samples: int = 6,
) -> list[tuple[float, float]]:
    """构造整圈渐开线直齿轮的二维外轮廓。

    这个函数尝试一次性生成完整外边界，适合后续做“先轮廓、后拉伸”的建模。
    当前项目里真正用于生成实体的主流程仍然是 `build_tooth_outline()`
    加周向阵列并集，但这里保留整圈轮廓函数以便继续优化。
    """
    validate_spur_gear_spec(spec)

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

    # 单边齿厚在分度圆上的半角；侧隙会使齿厚略微减小
    pitch_half_angle = (math.pi / (2.0 * spec.tooth_count)) - (spec.backlash / (2.0 * spec.pitch_radius))
    if pitch_half_angle <= 0:
        raise ValueError("backlash is too large for the given gear")

    # 将标准渐开线旋转到分度圆齿厚所对应的位置
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


def build_internal_tooth_space_outline(
    spec: InternalRingGearSpec,
    involute_samples: int = 12,
    root_arc_samples: int = 6,
    tip_arc_samples: int = 6,
) -> list[tuple[float, float]]:
    """构造内齿圈单个齿槽切刀的二维闭合轮廓。

    该轮廓以 +X 方向为齿槽中心线，从内齿齿顶圆切到内齿齿根圆。
    """
    validate_internal_ring_gear_spec(spec)

    # 内齿圈齿槽在分度圆处略大于半齿厚，以给外齿轮啮合留出侧隙。
    space_half_angle = (math.pi / (2.0 * spec.tooth_count)) + (spec.backlash / (2.0 * spec.pitch_radius))
    if space_half_angle >= spec.tooth_pitch_angle * 0.5:
        raise ValueError("backlash is too large for the given internal ring gear")

    pitch_involute_angle = involute_polar_angle(spec.base_radius, spec.pitch_radius)
    flank_phase = space_half_angle + pitch_involute_angle
    outer_involute_angle = flank_phase - involute_polar_angle(spec.base_radius, spec.dedendum_radius)

    if spec.addendum_radius >= spec.base_radius:
        involute_start_radius = spec.addendum_radius
        involute_start_angle = flank_phase - involute_polar_angle(spec.base_radius, involute_start_radius)
        needs_tip_connector = False
    else:
        involute_start_radius = spec.base_radius
        involute_start_angle = flank_phase
        needs_tip_connector = True

    upper_tip = polar_to_cartesian(spec.addendum_radius, involute_start_angle)
    lower_tip = polar_to_cartesian(spec.addendum_radius, -involute_start_angle)

    raw_flank = involute_curve_points(
        spec.base_radius,
        involute_start_radius,
        spec.dedendum_radius,
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

    outline: list[tuple[float, float]] = [upper_tip]
    if needs_tip_connector:
        outline.append(polar_to_cartesian(spec.base_radius, involute_start_angle))

    outline.extend(upper_flank[1:] if upper_flank else [])
    outline.extend(
        sample_circular_arc(
            spec.dedendum_radius,
            outer_involute_angle,
            -outer_involute_angle,
            root_arc_samples,
            include_start=False,
            include_end=False,
        )
    )
    outline.extend(lower_flank)

    if needs_tip_connector:
        outline.append(lower_tip)

    outline.extend(
        sample_circular_arc(
            spec.addendum_radius,
            -involute_start_angle,
            involute_start_angle,
            tip_arc_samples,
            include_start=False,
            include_end=False,
        )
    )

    return _dedupe_points(outline)


def build_spur_gear(
    spec: SpurGearSpec,
    plane: str = "XY",
    involute_samples: int = 12,
    root_arc_samples: int = 6,
    tip_arc_samples: int = 6,
) -> cq.Workplane:
    """根据参数直接生成三维直齿轮实体。"""
    validate_spur_gear_spec(spec)

    gear = cq.Workplane(plane).circle(spec.dedendum_radius).extrude(spec.thickness * 0.5, both=True)
    tooth_outline = build_tooth_outline(
        spec,
        involute_samples=involute_samples,
        tip_arc_samples=tip_arc_samples,
    )
    tooth = extrude_profile(plane, tooth_outline, spec.thickness)
    for tooth_index in range(spec.tooth_count):
        angle_deg = tooth_index * 360.0 / spec.tooth_count
        gear = gear.union(
            tooth.rotate((0, 0, 0), (0, 0, 1), angle_deg),
            clean=False,
        )

    if spec.bore_diameter and spec.bore_diameter > 0:
        cutter = cq.Workplane(plane).circle(spec.bore_diameter * 0.5)
        gear = gear.cut(cutter.extrude(spec.thickness * 0.75, both=True))

    if spec.sector_angle_deg < 360.0:
        sector_cutter = _build_sector_cutter(spec, plane)
        gear = gear.intersect(sector_cutter)

    solid = gear.solids().val()
    return cq.Workplane(plane).newObject([solid])


def build_internal_ring_gear(
    spec: InternalRingGearSpec,
    plane: str = "XY",
    involute_samples: int = 12,
    root_arc_samples: int = 6,
    tip_arc_samples: int = 6,
) -> cq.Workplane:
    """根据参数直接生成三维内齿圈实体。"""
    validate_internal_ring_gear_spec(spec)

    ring = cq.Workplane(plane).circle(spec.outer_radius).extrude(spec.thickness * 0.5, both=True)
    bore_cutter = cq.Workplane(plane).circle(spec.addendum_radius).extrude(spec.thickness * 0.75, both=True)
    ring = ring.cut(bore_cutter)

    tooth_space_outline = build_internal_tooth_space_outline(
        spec,
        involute_samples=involute_samples,
        root_arc_samples=root_arc_samples,
        tip_arc_samples=tip_arc_samples,
    )
    tooth_space = extrude_profile(plane, tooth_space_outline, spec.thickness * 1.5)
    for tooth_index in range(spec.tooth_count):
        angle_deg = tooth_index * 360.0 / spec.tooth_count
        ring = ring.cut(
            tooth_space.rotate((0, 0, 0), (0, 0, 1), angle_deg),
            clean=False,
        )

    if spec.sector_angle_deg < 360.0:
        sector_cutter = _build_sector_cutter_by_radius(
            radius=spec.outer_radius * 1.05,
            thickness=spec.thickness,
            sector_angle_deg=spec.sector_angle_deg,
            plane=plane,
        )
        ring = ring.intersect(sector_cutter)

    solid = ring.solids().val()
    return cq.Workplane(plane).newObject([solid])


def build_spur_gear_blank(spec: SpurGearSpec, plane: str = "XY") -> cq.Workplane:
    """生成齿轮毛坯，用于对照渐开线齿形。"""
    validate_spur_gear_spec(spec)
    blank = cq.Workplane(plane).circle(spec.addendum_radius).extrude(spec.thickness * 0.5, both=True)
    if spec.bore_diameter and spec.bore_diameter > 0:
        blank = blank.cut(cq.Workplane(plane).circle(spec.bore_diameter * 0.5).extrude(spec.thickness * 0.75, both=True))
    if spec.sector_angle_deg < 360.0:
        blank = blank.intersect(_build_sector_cutter(spec, plane))
    return blank
