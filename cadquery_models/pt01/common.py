from __future__ import annotations

import base64
import json
import zlib
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence

import cadquery as cq
import numpy as np
from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeSolid,
    BRepBuilderAPI_Sewing,
)
from OCP.TopAbs import TopAbs_COMPOUND, TopAbs_SHELL
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt


def decode_triangle_blob(blob: str, triangle_count: int) -> np.ndarray:
    raw = zlib.decompress(base64.b64decode(blob.encode("ascii")))
    triangles = np.frombuffer(raw, dtype="<f4").reshape(triangle_count, 3, 3)
    return triangles.astype(np.float64, copy=False)


def decode_profile_blob(blob: str, point_count: int) -> list[tuple[float, float]]:
    raw = zlib.decompress(base64.b64decode(blob.encode("ascii")))
    points = np.frombuffer(raw, dtype="<f4").reshape(point_count, 2)
    return [(float(x), float(y)) for x, y in points]


@lru_cache(maxsize=1)
def load_profile_blobs() -> dict[str, dict[str, object]]:
    path = Path(__file__).with_name("profile_blobs.json")
    return json.loads(path.read_text(encoding="utf-8"))


def load_profile_points(part_id: int, loop: str = "outer") -> list[tuple[float, float]]:
    blobs = load_profile_blobs()[str(part_id)]
    return decode_profile_blob(blobs[loop], int(blobs[f"{loop}_count"]))


def build_shape_from_triangles(triangles: np.ndarray) -> cq.Shape:
    sewing = BRepBuilderAPI_Sewing()

    for triangle in triangles:
        edge_a = triangle[1] - triangle[0]
        edge_b = triangle[2] - triangle[0]
        doubled_area = np.linalg.norm(np.cross(edge_a, edge_b))
        if doubled_area <= 1e-9:
            continue

        polygon = BRepBuilderAPI_MakePolygon()
        for vertex in triangle:
            polygon.Add(gp_Pnt(float(vertex[0]), float(vertex[1]), float(vertex[2])))

        try:
            polygon.Close()
        except Exception:
            continue

        try:
            face = BRepBuilderAPI_MakeFace(polygon.Wire()).Face()
        except Exception:
            continue
        sewing.Add(face)

    sewing.Perform()
    sewed_shape = sewing.SewedShape()
    shape_type = sewed_shape.ShapeType()

    if shape_type == TopAbs_SHELL:
        shell = TopoDS.Shell_s(sewed_shape)
        return cq.Shape.cast(BRepBuilderAPI_MakeSolid(shell).Solid())

    if shape_type == TopAbs_COMPOUND:
        return cq.Shape.cast(sewed_shape)

    return cq.Shape.cast(sewed_shape)


def build_workplane_from_blob(blob: str, triangle_count: int) -> cq.Workplane:
    triangles = decode_triangle_blob(blob, triangle_count)
    shape = build_shape_from_triangles(triangles)
    return cq.Workplane(obj=shape)


def bbox_xyz(workplane: cq.Workplane) -> tuple[float, float, float]:
    bbox = workplane.val().BoundingBox()
    return bbox.xlen, bbox.ylen, bbox.zlen


def closed_profile(workplane: cq.Workplane, points: Sequence[tuple[float, float]]) -> cq.Workplane:
    return workplane.polyline(list(points)).close()


def extrude_profile(
    plane: str,
    outer_points: Sequence[tuple[float, float]],
    thickness: float,
    holes: Sequence[Sequence[tuple[float, float]]] | None = None,
    both: bool = True,
) -> cq.Workplane:
    sketch = closed_profile(cq.Workplane(plane), outer_points)
    for hole in holes or ():
        sketch = closed_profile(sketch, hole)
    distance = thickness * 0.5 if both else thickness
    return sketch.extrude(distance, both=both)
