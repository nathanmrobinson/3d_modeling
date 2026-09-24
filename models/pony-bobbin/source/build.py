#!/usr/bin/env python3
"""Build a simplified P60624-style bobbin in millimetres, lying flat in XY."""

from pathlib import Path
import hashlib
import json
import math

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Polygon, box
from shapely.geometry.polygon import orient
import trimesh


MODEL_DIR = Path(__file__).resolve().parents[1]
WIDTH = 25.0
LENGTH = 65.0
THICKNESS = 1.0
SLIT_WIDTH = 0.6
SLIT_X = WIDTH / 2 + 2.0  # Slightly right of centre, as in the reference.
CORNER_RADIUS = 1.2
EYE_RADIUS = 7.1
EYE_BASE_Y = 47.0
EYE_SPRING_Y = 49.2
FORK_DEPTH = 10.5
FORK_INNER_WIDTH = 13.0
FORK_MOUTH_WIDTH = 17.0
TOP_NOTCH_DEPTH = 4.5


def make_profile():
    """Use straight segments and one circular arch, ignoring photo artefacts."""
    outer = Polygon([
        (0, 0),
        ((WIDTH - FORK_MOUTH_WIDTH) / 2, 0),
        ((WIDTH - FORK_INNER_WIDTH) / 2, FORK_DEPTH),
        ((WIDTH + FORK_INNER_WIDTH) / 2, FORK_DEPTH),
        ((WIDTH + FORK_MOUTH_WIDTH) / 2, 0),
        (WIDTH, 0),
        (WIDTH, LENGTH),
        (SLIT_X + SLIT_WIDTH / 2, LENGTH - TOP_NOTCH_DEPTH),
        (SLIT_X - SLIT_WIDTH / 2, LENGTH - TOP_NOTCH_DEPTH),
        (0, LENGTH),
    ])
    # Round the projecting tips for handling, retaining straight side edges.
    outer = outer.buffer(-CORNER_RADIUS, quad_segs=12).buffer(
        CORNER_RADIUS, quad_segs=12
    ).simplify(0.002, preserve_topology=True)
    xmin, ymin, xmax, ymax = outer.bounds
    outer = affinity.translate(outer, -xmin, -ymin)
    outer = affinity.scale(
        outer, xfact=WIDTH / (xmax - xmin),
        yfact=LENGTH / (ymax - ymin), origin=(0, 0)
    )

    # D-shaped eye: a horizontal bottom, short vertical walls, circular roof.
    arch = [
        (WIDTH / 2 + EYE_RADIUS * math.cos(a),
         EYE_SPRING_Y + EYE_RADIUS * math.sin(a))
        for a in np.linspace(0, math.pi, 65)
    ]
    eye = Polygon([
        (WIDTH / 2 - EYE_RADIUS, EYE_BASE_Y),
        (WIDTH / 2 + EYE_RADIUS, EYE_BASE_Y),
        *arch,
    ])
    # Subtract the slit last: it overlaps the eye and extends past the top.
    # This is an actual empty channel through the solid, not a surface seam.
    slit = box(SLIT_X - SLIT_WIDTH / 2, EYE_BASE_Y + 0.5,
               SLIT_X + SLIT_WIDTH / 2, LENGTH + 2)
    profile = orient(outer.difference(eye.union(slit)), sign=1.0)
    assert profile.is_valid and profile.geom_type == "Polygon"
    assert len(profile.interiors) == 0, "Eye must connect to the outside."
    assert profile.intersection(LineString([
        (SLIT_X, EYE_BASE_Y + 1), (SLIT_X, LENGTH + 1)
    ])).is_empty, "Slit must remain open."
    return profile


def main():
    profile = make_profile()
    mesh = trimesh.creation.extrude_polygon(profile, THICKNESS, engine="earcut")
    mesh.metadata.update(units="mm", name="Pony-style yarn bobbin")
    exports = MODEL_DIR / "exports"
    exports.mkdir(parents=True, exist_ok=True)
    stem = "pony-bobbin-65x25x1mm"
    stl = exports / f"{stem}.stl"
    mesh.export(stl)
    (exports / f"{stem}.3mf").write_bytes(
        trimesh.exchange.threemf.export_3MF(mesh)
    )

    # Validate the actual exported STL, not just the construction polygon.
    exported = trimesh.load_mesh(stl, process=True)
    assert exported.is_watertight and exported.is_winding_consistent
    assert exported.is_volume and len(exported.split()) == 1
    assert np.all(exported.area_faces > 1e-10)
    assert np.allclose(exported.extents, [WIDTH, LENGTH, THICKNESS], atol=1e-5)
    assert np.isclose(exported.bounds[0, 2], 0)

    # Each section must have one exterior contour and no enclosed eye hole.
    for z in (0.1, 0.5, 0.9):
        section = exported.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        assert len(section.discrete) == 1

    gap = exported.section(
        plane_origin=[0, 58, 0], plane_normal=[0, 1, 0]
    )
    left, right = sorted(gap.discrete, key=lambda points: points[:, 0].mean())
    measured_gap = float(right[:, 0].min() - left[:, 0].max())
    assert np.isclose(measured_gap, SLIT_WIDTH, atol=1e-5)

    # Portable, editable outline for inspecting the same profile in CAD.
    points = list(profile.exterior.coords)[:-1]
    (MODEL_DIR / "source" / "outline.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="25mm" height="65mm" '
        'viewBox="0 0 25 65">\n'
        '<path fill="#cf6439" d="M ' + ' L '.join(
            f'{x:.5f},{LENGTH-y:.5f}' for x, y in points
        ) + ' Z"/>\n</svg>\n'
    )
    report = {
        "stl_sha256": hashlib.sha256(stl.read_bytes()).hexdigest(),
        "size_mm_xyz": exported.extents.tolist(),
        "watertight": bool(exported.is_watertight),
        "consistent_normals": bool(exported.is_winding_consistent),
        "solid_components": len(exported.split()),
        "triangles": len(exported.faces),
        "volume_mm3": round(float(exported.volume), 3),
        "slit_width_mm_measured_from_stl": round(measured_gap, 6),
        "eye_open_to_outside": True,
        "bed_contact_z_mm": float(exported.bounds[0, 2]),
        "physically_printed": False,
    }
    (MODEL_DIR / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
