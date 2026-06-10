from __future__ import annotations

"""Export a 10:1 planetary gear set with an outer diameter of about 100 mm.

Usage:
    .venv\\Scripts\\python.exe cadquery_models\\example\\test_step\\planetary_gear.py

The script exports each part as a STEP file under test_step/exports.
The reduction ratio assumes a fixed ring gear, sun input, and carrier output:
    ratio = 1 + ring_teeth / sun_teeth = 10:1
"""

import math
from pathlib import Path
import sys

import cadquery as cq


CURRENT_DIR = Path(__file__).resolve().parent
EXAMPLE_DIR = CURRENT_DIR.parent
if str(EXAMPLE_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLE_DIR))

from gear_generator import (  # noqa: E402
    InternalRingGearSpec,
    SpurGearSpec,
    build_internal_ring_gear,
    build_spur_gear,
)


# =========================
# Planetary gear parameters
# =========================

MODULE = 0.88
PRESSURE_ANGLE_DEG = 20.0
BACKLASH = 0.08

SUN_TEETH = 12
PLANET_TEETH = 48
RING_TEETH = SUN_TEETH + 2 * PLANET_TEETH
PLANET_COUNT = 3

GEAR_THICKNESS = 8.0
RING_OUTER_DIAMETER = 100.0

SUN_BORE_DIAMETER = 5.0
PLANET_BORE_DIAMETER = 4.0
CARRIER_CENTER_BORE_DIAMETER = 8.0
CARRIER_PIN_HOLE_DIAMETER = 4.0

CARRIER_THICKNESS = 3.0
CARRIER_OUTER_DIAMETER = 86.0
CARRIER_CLEARANCE = 0.5
CARRIER_Z = GEAR_THICKNESS * 0.5 + CARRIER_CLEARANCE + CARRIER_THICKNESS * 0.5

INPUT_SHAFT_DIAMETER = 4.8
INPUT_SHAFT_LENGTH = 28.0
INPUT_SHAFT_CENTER_Z = -8.0

OUTPUT_SHAFT_DIAMETER = 7.8
OUTPUT_SHAFT_LENGTH = 28.0
OUTPUT_FLANGE_DIAMETER = 22.0
OUTPUT_FLANGE_THICKNESS = 4.0
OUTPUT_FLANGE_BOLT_COUNT = 3
OUTPUT_FLANGE_BOLT_CIRCLE_DIAMETER = 16.0
OUTPUT_FLANGE_BOLT_HOLE_DIAMETER = 2.4

PLANET_PIN_DIAMETER = 3.8
PLANET_PIN_REAR_Z = -GEAR_THICKNESS * 0.5 - 0.5
PLANET_PIN_FRONT_Z = CARRIER_Z + CARRIER_THICKNESS * 0.5 + 0.5
PLANET_PIN_LENGTH = PLANET_PIN_FRONT_Z - PLANET_PIN_REAR_Z
PLANET_PIN_CENTER_Z = (PLANET_PIN_FRONT_Z + PLANET_PIN_REAR_Z) * 0.5

RING_MOUNT_OUTER_DIAMETER = 116.0
RING_MOUNT_INNER_DIAMETER = RING_OUTER_DIAMETER + 0.6
RING_MOUNT_THICKNESS = GEAR_THICKNESS
RING_MOUNT_BOLT_COUNT = 4
RING_MOUNT_BOLT_CIRCLE_DIAMETER = 106.0
RING_MOUNT_BOLT_HOLE_DIAMETER = 4.2


# =========================
# Curve sampling
# =========================

INVOLUTE_SAMPLES = 10
TIP_ARC_SAMPLES = 6
ROOT_ARC_SAMPLES = 6


SUN_SPEC = SpurGearSpec(
    module=MODULE,
    tooth_count=SUN_TEETH,
    thickness=GEAR_THICKNESS,
    pressure_angle_deg=PRESSURE_ANGLE_DEG,
    bore_diameter=SUN_BORE_DIAMETER,
    backlash=BACKLASH,
)

PLANET_SPEC = SpurGearSpec(
    module=MODULE,
    tooth_count=PLANET_TEETH,
    thickness=GEAR_THICKNESS,
    pressure_angle_deg=PRESSURE_ANGLE_DEG,
    bore_diameter=PLANET_BORE_DIAMETER,
    backlash=BACKLASH,
)

RING_SPEC = InternalRingGearSpec(
    module=MODULE,
    tooth_count=RING_TEETH,
    thickness=GEAR_THICKNESS,
    outer_diameter=RING_OUTER_DIAMETER,
    pressure_angle_deg=PRESSURE_ANGLE_DEG,
    backlash=BACKLASH,
)


def planetary_ratio() -> float:
    """Return fixed-ring planetary ratio for sun input and carrier output."""
    return 1.0 + RING_TEETH / SUN_TEETH


def planet_center_radius() -> float:
    """Return the sun-to-planet center distance."""
    return MODULE * (SUN_TEETH + PLANET_TEETH) * 0.5


def planet_positions() -> list[tuple[float, float, float]]:
    """Return planet center positions as x, y, angle_deg."""
    radius = planet_center_radius()
    return [
        (
            radius * math.cos(2.0 * math.pi * index / PLANET_COUNT),
            radius * math.sin(2.0 * math.pi * index / PLANET_COUNT),
            360.0 * index / PLANET_COUNT,
        )
        for index in range(PLANET_COUNT)
    ]


def z_cylinder(
    diameter: float,
    length: float,
    *,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
) -> cq.Workplane:
    """Build a Z-axis cylinder centered at the given assembly coordinate."""
    return (
        cq.Workplane("XY")
        .center(x, y)
        .circle(diameter * 0.5)
        .extrude(length * 0.5, both=True)
        .translate((0, 0, z))
    )


def build_sun_gear() -> cq.Workplane:
    """Build the sun gear at the assembly origin."""
    return build_spur_gear(
        SUN_SPEC,
        involute_samples=INVOLUTE_SAMPLES,
        root_arc_samples=ROOT_ARC_SAMPLES,
        tip_arc_samples=TIP_ARC_SAMPLES,
    )


def build_planet_gear() -> cq.Workplane:
    """Build one planet gear centered at the local origin."""
    return build_spur_gear(
        PLANET_SPEC,
        involute_samples=INVOLUTE_SAMPLES,
        root_arc_samples=ROOT_ARC_SAMPLES,
        tip_arc_samples=TIP_ARC_SAMPLES,
    )


def build_planet_gear_at(x: float, y: float, angle_deg: float) -> cq.Workplane:
    """Build one planet gear placed in assembly coordinates."""
    mesh_phase_deg = 180.0 / PLANET_TEETH
    return (
        build_planet_gear()
        .rotate((0, 0, 0), (0, 0, 1), angle_deg + mesh_phase_deg)
        .translate((x, y, 0))
    )


def build_ring_gear() -> cq.Workplane:
    """Build the fixed internal ring gear at the assembly origin."""
    return build_internal_ring_gear(
        RING_SPEC,
        involute_samples=INVOLUTE_SAMPLES,
        root_arc_samples=ROOT_ARC_SAMPLES,
        tip_arc_samples=TIP_ARC_SAMPLES,
    )


def build_sun_input_shaft() -> cq.Workplane:
    """Build the input shaft that passes through the sun gear bore."""
    return z_cylinder(
        INPUT_SHAFT_DIAMETER,
        INPUT_SHAFT_LENGTH,
        z=INPUT_SHAFT_CENTER_Z,
    )


def build_output_shaft() -> cq.Workplane:
    """Build an output shaft with a small flange for the carrier."""
    shaft_start_z = CARRIER_Z + CARRIER_THICKNESS * 0.5
    shaft_center_z = shaft_start_z + OUTPUT_SHAFT_LENGTH * 0.5
    flange_center_z = shaft_start_z + OUTPUT_FLANGE_THICKNESS * 0.5

    shaft = z_cylinder(
        OUTPUT_SHAFT_DIAMETER,
        OUTPUT_SHAFT_LENGTH,
        z=shaft_center_z,
    )
    flange = z_cylinder(
        OUTPUT_FLANGE_DIAMETER,
        OUTPUT_FLANGE_THICKNESS,
        z=flange_center_z,
    )
    output = shaft.union(flange)

    bolt_radius = OUTPUT_FLANGE_BOLT_CIRCLE_DIAMETER * 0.5
    for index in range(OUTPUT_FLANGE_BOLT_COUNT):
        angle = 2.0 * math.pi * index / OUTPUT_FLANGE_BOLT_COUNT
        x = bolt_radius * math.cos(angle)
        y = bolt_radius * math.sin(angle)
        bolt_hole = z_cylinder(
            OUTPUT_FLANGE_BOLT_HOLE_DIAMETER,
            OUTPUT_FLANGE_THICKNESS * 1.5,
            x=x,
            y=y,
            z=flange_center_z,
        )
        output = output.cut(bolt_hole)

    return output


def build_planet_pin_at(x: float, y: float) -> cq.Workplane:
    """Build one planet pin in assembly coordinates."""
    return z_cylinder(
        PLANET_PIN_DIAMETER,
        PLANET_PIN_LENGTH,
        x=x,
        y=y,
        z=PLANET_PIN_CENTER_Z,
    )


def build_ring_mount() -> cq.Workplane:
    """Build a fixed outer mount that can hold the ring gear in place."""
    mount = z_cylinder(RING_MOUNT_OUTER_DIAMETER, RING_MOUNT_THICKNESS)
    mount = mount.cut(z_cylinder(RING_MOUNT_INNER_DIAMETER, RING_MOUNT_THICKNESS * 1.5))

    bolt_radius = RING_MOUNT_BOLT_CIRCLE_DIAMETER * 0.5
    for index in range(RING_MOUNT_BOLT_COUNT):
        angle = 2.0 * math.pi * index / RING_MOUNT_BOLT_COUNT
        x = bolt_radius * math.cos(angle)
        y = bolt_radius * math.sin(angle)
        bolt_hole = z_cylinder(
            RING_MOUNT_BOLT_HOLE_DIAMETER,
            RING_MOUNT_THICKNESS * 1.5,
            x=x,
            y=y,
        )
        mount = mount.cut(bolt_hole)

    return mount


def build_carrier() -> cq.Workplane:
    """Build a carrier plate with center shaft, pin, and flange bolt holes."""
    carrier = (
        cq.Workplane("XY")
        .circle(CARRIER_OUTER_DIAMETER * 0.5)
        .extrude(CARRIER_THICKNESS * 0.5, both=True)
    )
    carrier = carrier.cut(
        cq.Workplane("XY")
        .circle(CARRIER_CENTER_BORE_DIAMETER * 0.5)
        .extrude(CARRIER_THICKNESS * 0.75, both=True)
    )

    for x, y, angle_deg in planet_positions():
        pin_hole = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(CARRIER_PIN_HOLE_DIAMETER * 0.5)
            .extrude(CARRIER_THICKNESS * 0.75, both=True)
        )
        carrier = carrier.cut(pin_hole)

    bolt_radius = OUTPUT_FLANGE_BOLT_CIRCLE_DIAMETER * 0.5
    for index in range(OUTPUT_FLANGE_BOLT_COUNT):
        angle = 2.0 * math.pi * index / OUTPUT_FLANGE_BOLT_COUNT
        bolt_hole = (
            cq.Workplane("XY")
            .center(bolt_radius * math.cos(angle), bolt_radius * math.sin(angle))
            .circle(OUTPUT_FLANGE_BOLT_HOLE_DIAMETER * 0.5)
            .extrude(CARRIER_THICKNESS * 0.75, both=True)
        )
        carrier = carrier.cut(bolt_hole)

    return carrier.translate((0, 0, CARRIER_Z))


def build_all_parts() -> dict[str, cq.Workplane]:
    """Build every exported part in assembly coordinates."""
    parts: dict[str, cq.Workplane] = {
        "sun_gear": build_sun_gear(),
        "ring_gear": build_ring_gear(),
        "ring_mount": build_ring_mount(),
        "carrier": build_carrier(),
        "sun_input_shaft": build_sun_input_shaft(),
        "carrier_output_shaft": build_output_shaft(),
    }

    for index, (x, y, angle_deg) in enumerate(planet_positions(), start=1):
        parts[f"planet_gear_{index}"] = build_planet_gear_at(x, y, angle_deg)
        parts[f"planet_pin_{index}"] = build_planet_pin_at(x, y)

    return parts


def export_step() -> list[Path]:
    """Export every part STEP file and return the generated paths."""
    export_dir = CURRENT_DIR / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    exported_paths: list[Path] = []
    for name, part in build_all_parts().items():
        export_path = export_dir / f"planetary_{name}.step"
        cq.exporters.export(part, str(export_path))
        exported_paths.append(export_path)

    return exported_paths


def main() -> None:
    print("planetary gear set")
    print(f"module: {MODULE:.3f} mm")
    print(f"teeth: sun={SUN_TEETH}, planet={PLANET_TEETH}, ring={RING_TEETH}")
    print(f"planet count: {PLANET_COUNT}")
    print(f"outer diameter: {RING_OUTER_DIAMETER:.1f} mm")
    print(f"fixed-ring ratio: {planetary_ratio():.2f}:1")
    print(f"planet center radius: {planet_center_radius():.3f} mm")

    for path in export_step():
        print(f"exported: {path}")


if __name__ == "__main__":
    main()
