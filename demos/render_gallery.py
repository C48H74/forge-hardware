"""Render presentation cards from exported tessellations; no generated/imagined geometry.
Run from repository root after building the three showcase examples.
"""

from pathlib import Path
import json
import runpy
import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont
from forge_hardware.robot import zero_transforms

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demos" / "images"
BG = (12, 22, 35)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    try:
        return ImageFont.truetype(BOLD if bold else FONT, size)
    except OSError:
        return ImageFont.load_default(size=size)


def raster(scene, size=(1150, 820), offsets=None, camera=(1, -1, 0.95)):
    width, height = size
    n = np.asarray(camera, float)
    n /= np.linalg.norm(n)
    right = np.cross([0, 0, 1], n)
    right /= np.linalg.norm(right)
    up = np.cross(n, right)
    projection = np.stack([right, -up, n], axis=1)
    fk = zero_transforms(scene["robot"]) if scene.get("robot") else {}
    parts = []
    for p in scene["parts"]:
        vs = np.asarray(p["vertices"], float)
        m = fk.get(p["id"], np.eye(4))
        world = (
            vs @ m[:3, :3].T
            + m[:3, 3] * 1000
            + np.asarray((offsets or {}).get(p["id"], [0, 0, 0]))
        )
        parts.append((p, world, world @ projection))
    allpts = np.concatenate([r[2] for r in parts])
    lo = allpts[:, :2].min(0)
    hi = allpts[:, :2].max(0)
    scale = min(
        (width - 100) / max(hi[0] - lo[0], 1), (height - 100) / max(hi[1] - lo[1], 1)
    )
    img = np.zeros((height, width, 4), np.uint8)
    depth = np.full((height, width), -np.inf)
    light = np.asarray([-0.2, -0.5, 1.0], float)
    light /= np.linalg.norm(light)
    for p, world, vertices in parts:
        vertices[:, :2] = (vertices[:, :2] - (lo + hi) / 2) * scale + [
            width / 2,
            height / 2,
        ]
        color = np.asarray(ImageColor.getrgb(p["color"])[:3])
        for f in p["triangles"]:
            a, b, c = vertices[f]
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
            if abs(den) < 1e-10:
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
            norm = np.cross(world[f[1]] - world[f[0]], world[f[2]] - world[f[0]])
            norm /= max(np.linalg.norm(norm), 1e-10)
            shade = 0.46 + 0.54 * abs(float(norm @ light))
            region[mask] = z[mask]
            sub = img[y0 : y1 + 1, x0 : x1 + 1]
            sub[mask, :3] = np.clip(color * shade, 0, 255).astype(np.uint8)
            sub[mask, 3] = 255
    return Image.fromarray(img)


DATA = {
    "gearbox_housing": dict(
        index="01",
        title="Split bearing housing",
        subtitle="Carcaça bipartida  /  Carcasa partida",
        eyebrow="MACHINED ASSEMBLY",
        facts=[
            ("04", "separate solids"),
            ("08", "lid bolt locations"),
            ("52 mm", "bearing-seat diameter"),
            ("180 mm", "housing length"),
        ],
        details=[
            "Ribbed shells + mounting feet",
            "Removable cover + locating pins",
            "Named bearing and bolt references",
        ],
        color="#66C4CD",
        view="Exploded inspection view",
    ),
    "parallel_gripper": dict(
        index="02",
        title="Parallel robotic gripper",
        subtitle="Garra robótica paralela  /  Pinza robótica paralela",
        eyebrow="ROBOT INTERCHANGE",
        facts=[
            ("09", "separate solids"),
            ("02", "prismatic joints"),
            ("20 mm", "travel per carriage"),
            ("50 mm", "baseline finger length"),
        ],
        details=[
            "Pocketed fingers + serrated pads",
            "Local link frames + SI properties",
            "URDF / SRDF / SDF exports",
        ],
        color="#EEAC55",
        view="Assembled zero-position view",
    ),
    "cooling_manifold": dict(
        index="03",
        title="Serpentine cooling plate",
        subtitle="Bloco de refrigeração  /  Placa de refrigeración",
        eyebrow="INTERNAL FLOW GEOMETRY",
        facts=[
            ("06", "connected channel passes"),
            ("09", "integral cooling fins"),
            ("08", "cover bolt locations"),
            ("7 mm", "channel depth"),
        ],
        details=[
            "Seal recess + counterbored cover",
            "Two fluid ports + explicit flat profile",
            "Internal channels revealed by lifting lid",
        ],
        color="#66C4CD",
        view="Exploded inspection view",
    ),
}


def card(name):
    info = DATA[name]
    scene = json.loads((ROOT / "build" / name / "scene.json").read_text())
    source = runpy.run_path(str(ROOT / "examples" / f"{name}.py"))
    offsets = (
        source.get("exploded_display_offsets", {}) if name != "parallel_gripper" else {}
    )
    # Render at twice the display resolution for antialiasing.
    model = raster(scene, (2240, 1600), offsets=offsets).resize(
        (1120, 800), Image.Resampling.LANCZOS
    )
    im = Image.new("RGB", (1600, 1200), BG)
    d = ImageDraw.Draw(im)
    d.text((55, 32), "FORGE / HARDWARE", font=font(25, True), fill="#78D7C4")
    d.text((55, 86), info["title"], font=font(49, True), fill="#F1F5FA")
    d.text((57, 154), info["subtitle"], font=font(19), fill="#91AABD")
    d.rounded_rectangle((1290, 44, 1545, 87), radius=18, fill="#183443")
    d.text((1310, 54), "REAL CAD GEOMETRY", font=font(16, True), fill="#8CE2CD")
    d.line((55, 205, 1545, 205), fill="#284051", width=2)
    for x in range(55, 1170, 56):
        d.line((x, 235, x, 1050), fill="#102031")
    for y in range(260, 1050, 56):
        d.line((45, y, 1170, y), fill="#102031")
    im.paste(model, (35, 240), model)
    d = ImageDraw.Draw(im)
    d.text((70, 245), info["view"].upper(), font=font(14, True), fill="#6E8DA4")
    d.text((1205, 250), info["eyebrow"], font=font(16, True), fill=info["color"])
    y = 302
    for number, label in info["facts"]:
        d.text((1205, y), number, font=font(44, True), fill="#F0F5FA")
        d.text((1207, y + 58), label, font=font(17), fill="#9CB1C3")
        y += 140
    d.line((1205, 895, 1540, 895), fill="#284051", width=2)
    for y, text in enumerate(info["details"]):
        # Wrap sidebar details to prevent overflow.
        words = text.split()
        line = ""
        lines = []
        for word in words:
            new = (line + " " + word).strip()
            if d.textlength(new, font=font(16)) > 325:
                lines.append(line)
                line = word
            else:
                line = new
        lines.append(line)
        for j, line in enumerate(lines):
            d.text((1205, 925 + y * 54 + j * 20), line, font=font(16), fill="#9DB2C4")
    d.line((55, 1080, 1545, 1080), fill="#284051", width=2)
    d.text(
        (58, 1101),
        "EDITABLE PYTHON  →  STEP  /  STL  /  3MF  /  GLB",
        font=font(20, True),
        fill="#C6D8E5",
    )
    d.text(
        (58, 1142),
        "Engineering demonstration · nominal geometry · no manufacturing or simulation certification",
        font=font(15),
        fill="#778FA4",
    )
    d.text((1450, 1093), info["index"], font=font(54, True), fill=info["color"])
    OUT.mkdir(parents=True, exist_ok=True)
    im.save(OUT / f"{name}.png", optimize=True)
    assembled = raster(scene, (1500, 1100))
    base = Image.new("RGBA", assembled.size, BG + (255,))
    base.alpha_composite(assembled)
    base.convert("RGB").save(OUT / f"{name}-assembled.png", optimize=True)
    return im


def main():
    cards = [card(n) for n in DATA]
    board = Image.new("RGB", (1920, 1080), BG)
    d = ImageDraw.Draw(board)
    d.text(
        (65, 40),
        "IDEA → EDITABLE CAD → VERIFIED EXPORTS",
        font=font(44, True),
        fill="#F0F5FA",
    )
    d.text(
        (67, 110),
        "FORGE HARDWARE     |     Three reproducible engineering demonstrations",
        font=font(23),
        fill="#83BFAF",
    )
    for i, im in enumerate(cards):
        board.paste(
            im.resize((600, 450), Image.Resampling.LANCZOS), (40 + i * 625, 225)
        )
    labels = [
        "Split bearing housing",
        "Parallel robotic gripper",
        "Serpentine cooling plate",
    ]
    for i, label in enumerate(labels):
        d.text((65 + i * 625, 710), label, font=font(23, True), fill="#D8E8F0")
    d.text((65, 805), "PARAMETRIC SOURCES", font=font(22, True), fill="#72D5C0")
    d.text(
        (65, 851),
        "Named model references · repeatable regeneration · local inspection",
        font=font(25),
        fill="#B6C9D9",
    )
    d.text(
        (65, 923),
        "github.com/C48H74/forge-hardware",
        font=font(30, True),
        fill="#F0F5FA",
    )
    d.text(
        (65, 1003),
        "Actual exported geometry. Demonstration concepts; engineering qualification remains separate.",
        font=font(18),
        fill="#7D94A7",
    )
    board.save(OUT / "showcase.png", optimize=True)
    print("Rendered three presentation cards, three assembly views and an overview.")


if __name__ == "__main__":
    main()
