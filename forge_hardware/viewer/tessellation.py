"""Render assets generated from exact BRep surfaces."""

import base64
import io
import numpy as np
from PIL import Image, ImageColor


def mesh(shape, tolerance=0.15):
    vertices, faces = shape.tessellate(tolerance)
    return {
        "vertices": [[float(v.X), float(v.Y), float(v.Z)] for v in vertices],
        "triangles": [list(f) for f in faces],
    }


def review_image(scene, target):
    """Orthographic geometry preview with a real per-pixel depth buffer."""
    width, height = 900, 800
    parts = []
    for p in scene["parts"]:
        vs = np.asarray(p.get("review_vertices", p["vertices"]), dtype=float)
        projected = np.column_stack(
            (
                0.7071 * (vs[:, 0] - vs[:, 1]),
                0.4082 * (vs[:, 0] + vs[:, 1]) - 0.8165 * vs[:, 2],
                vs.sum(axis=1),
            )
        )
        parts.append((p, vs, projected))
    allpts = np.concatenate([p[2] for p in parts])
    lo, hi = allpts[:, :2].min(axis=0), allpts[:, :2].max(axis=0)
    scale = 650 / max(*(hi - lo), 1)
    image = np.empty((height, width, 3), dtype=np.uint8)
    image[:] = [16, 26, 39]
    depth = np.full((height, width), -np.inf)
    light = np.array([0.3, -0.5, 1])
    light /= np.linalg.norm(light)
    for part, world, vertices in parts:
        vertices[:, :2] = (vertices[:, :2] - (lo + hi) / 2) * scale + [
            width / 2,
            height / 2,
        ]
        color = np.array(ImageColor.getrgb(part["color"])[:3])
        for face in part["triangles"]:
            a, b, c = vertices[face]
            x0, y0 = np.maximum(
                np.floor(np.minimum(np.minimum(a[:2], b[:2]), c[:2])).astype(int), 0
            )
            x1, y1 = np.minimum(
                np.ceil(np.maximum(np.maximum(a[:2], b[:2]), c[:2])).astype(int),
                [width - 1, height - 1],
            )
            if x0 > x1 or y0 > y1:
                continue
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-12:
                continue
            yy, xx = np.mgrid[y0 : y1 + 1, x0 : x1 + 1]
            xx = xx + 0.5
            yy = yy + 0.5
            u = ((b[1] - c[1]) * (xx - c[0]) + (c[0] - b[0]) * (yy - c[1])) / den
            v = ((c[1] - a[1]) * (xx - c[0]) + (a[0] - c[0]) * (yy - c[1])) / den
            w = 1 - u - v
            z = u * a[2] + v * b[2] + w * c[2]
            region = depth[y0 : y1 + 1, x0 : x1 + 1]
            mask = (u >= -1e-9) & (v >= -1e-9) & (w >= -1e-9) & (z > region)
            normal = np.cross(
                world[face[1]] - world[face[0]], world[face[2]] - world[face[0]]
            )
            norm = np.linalg.norm(normal)
            shade = 0.55 + 0.45 * abs(np.dot(normal / norm, light)) if norm else 0.7
            region[mask] = z[mask]
            image[y0 : y1 + 1, x0 : x1 + 1][mask] = (color * shade).astype(np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(image).save(buffer, format="PNG")
    target.with_suffix(".png").write_bytes(buffer.getvalue())
    encoded = base64.b64encode(buffer.getvalue()).decode()
    target.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="800"><image href="data:image/png;base64,{encoded}" width="900" height="800"/></svg>'
    )
