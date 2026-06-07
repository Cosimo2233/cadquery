from __future__ import annotations

import math
from typing import Iterable

import cadquery as cq


def polar_positions(count: int, radius: float, start_angle: float = 0.0) -> list[tuple[float, float, float]]:
    values: list[tuple[float, float, float]] = []
    for index in range(count):
        angle = math.radians(start_angle + 360.0 * index / count)
        values.append((radius * math.cos(angle), radius * math.sin(angle), math.degrees(angle)))
    return values


def union_all(base: cq.Workplane, solids: Iterable[cq.Workplane]) -> cq.Workplane:
    result = base
    for solid in solids:
        result = result.union(solid)
    return result


def cut_all(base: cq.Workplane, cutters: Iterable[cq.Workplane]) -> cq.Workplane:
    result = base
    for cutter in cutters:
        result = result.cut(cutter)
    return result


def tooth_tabs(
    plane: str,
    count: int,
    radius: float,
    radial_depth: float,
    tangential_width: float,
    thickness: float,
    start_angle: float = 0.0,
) -> list[cq.Workplane]:
    tabs: list[cq.Workplane] = []
    for x, y, angle_deg in polar_positions(count, radius + radial_depth * 0.5, start_angle):
        tabs.append(
            cq.Workplane(plane)
            .transformed(offset=(x, y, 0), rotate=(0, 0, angle_deg))
            .rect(radial_depth, tangential_width)
            .extrude(thickness * 0.5, both=True)
        )
    return tabs


def radial_ribs(
    plane: str,
    count: int,
    inner_radius: float,
    outer_radius: float,
    rib_width: float,
    thickness: float,
    start_angle: float = 0.0,
) -> list[cq.Workplane]:
    ribs: list[cq.Workplane] = []
    rib_length = outer_radius - inner_radius
    rib_center_radius = inner_radius + rib_length * 0.5
    for x, y, angle_deg in polar_positions(count, rib_center_radius, start_angle):
        ribs.append(
            cq.Workplane(plane)
            .transformed(offset=(x, y, 0), rotate=(0, 0, angle_deg))
            .rect(rib_length, rib_width)
            .extrude(thickness * 0.5, both=True)
        )
    return ribs


def rounded_slot_cutter(plane: str, length: float, diameter: float, depth: float) -> cq.Workplane:
    return cq.Workplane(plane).slot2D(length, diameter, 0).extrude(depth * 0.5, both=True)


def corner_holes(
    body: cq.Workplane,
    plane: str,
    width: float,
    height: float,
    offset_x: float,
    offset_y: float,
    diameter: float,
    depth: float,
) -> cq.Workplane:
    holes = (
        cq.Workplane(plane)
        .pushPoints(
            [
                (-width * 0.5 + offset_x, -height * 0.5 + offset_y),
                (width * 0.5 - offset_x, -height * 0.5 + offset_y),
                (-width * 0.5 + offset_x, height * 0.5 - offset_y),
                (width * 0.5 - offset_x, height * 0.5 - offset_y),
            ]
        )
        .circle(diameter * 0.5)
        .extrude(depth, both=True)
    )
    return body.cut(holes)


def simple_gear(
    plane: str,
    root_radius: float,
    tooth_count: int,
    tooth_height: float,
    tooth_width: float,
    thickness: float,
    bore_diameter: float,
    start_angle: float = 0.0,
) -> cq.Workplane:
    gear = cq.Workplane(plane).circle(root_radius).extrude(thickness * 0.5, both=True)
    gear = union_all(
        gear,
        tooth_tabs(
            plane=plane,
            count=tooth_count,
            radius=root_radius,
            radial_depth=tooth_height,
            tangential_width=tooth_width,
            thickness=thickness,
            start_angle=start_angle,
        ),
    )
    if bore_diameter > 0:
        gear = gear.cut(cq.Workplane(plane).circle(bore_diameter * 0.5).extrude(thickness * 1.25, both=True))
    return gear


def spoked_ring(
    plane: str,
    outer_radius: float,
    inner_radius: float,
    thickness: float,
    tooth_count: int,
    tooth_height: float,
    tooth_width: float,
    rib_count: int,
    rib_width: float,
    hub_radius: float,
) -> cq.Workplane:
    ring = cq.Workplane(plane).circle(outer_radius).circle(inner_radius).extrude(thickness * 0.5, both=True)
    ring = union_all(
        ring,
        tooth_tabs(
            plane=plane,
            count=tooth_count,
            radius=outer_radius,
            radial_depth=tooth_height,
            tangential_width=tooth_width,
            thickness=thickness,
            start_angle=360.0 / tooth_count * 0.5,
        ),
    )
    ring = ring.union(cq.Workplane(plane).circle(hub_radius).extrude(thickness * 0.5, both=True))
    ring = union_all(
        ring,
        radial_ribs(
            plane=plane,
            count=rib_count,
            inner_radius=hub_radius,
            outer_radius=inner_radius,
            rib_width=rib_width,
            thickness=thickness,
        ),
    )
    return ring
