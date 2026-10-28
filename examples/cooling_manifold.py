"""Parametric finned cold plate with an inspectable serpentine channel and cover.

Demonstration geometry, not a pressure-rated or thermally qualified product.
Nominal mm; plain bores represent fastener and fluid interfaces (no thread claim).
"""

from build123d import Box, Cylinder, Pos, Align, Rectangle, extrude
from forge_hardware.cad.build123d import Design, Part

exploded_display_offsets = {"cold_plate": [0, 0, 0], "cover": [0, 0, 38]}


def build(
    length=120,
    width=84,
    base_thickness=18,
    channel_width=5,
    channel_depth=7,
    cover_thickness=5,
    fin_height=12,
):
    if length < 100 or width < 80 or not 3 <= channel_width <= 6:
        raise ValueError("Use length >=100, width >=80, channel_width 3..6 mm")
    if (
        not 4 <= channel_depth <= base_thickness - 5
        or cover_thickness < 3
        or fin_height <= 0
    ):
        raise ValueError("Maintain channel floor >=5 mm and a cover >=3 mm")
    cmin = (Align.CENTER, Align.CENTER, Align.MIN)
    body = Box(length, width, base_thickness, align=cmin)
    run = length - 38
    ys = [-25, -15, -5, 5, 15, 25]
    # Six connected channel runs with alternating end returns.
    for y in ys:
        body -= Pos(0, y, base_thickness - channel_depth) * Box(
            run, channel_width, channel_depth + 1, align=cmin
        )
    for i in range(5):
        x = (run / 2 - channel_width / 2) * (1 if i % 2 == 0 else -1)
        body -= Pos(x, (ys[i] + ys[i + 1]) / 2, base_thickness - channel_depth) * Box(
            channel_width, 10 + channel_width, channel_depth + 1, align=cmin
        )
    # Rectangular demonstration seal groove surrounding the fluid paths.
    groove = extrude(
        Rectangle(length - 22, 66) - Rectangle(length - 26, 62), amount=1.4
    )
    body -= Pos(0, 0, base_thickness - 1.4) * groove
    for y in [-32, -24, -16, -8, 0, 8, 16, 24, 32]:
        body += Pos(0, y, -fin_height) * Box(
            length - 14, 2.4, fin_height + 0.2, align=cmin
        )
    features = {
        "channel_inlet": {
            "description": "Start of the six-pass serpentine coolant channel",
            "point": [-run / 2 + 4, ys[0], base_thickness - channel_depth / 2],
        },
        "channel_floor": {
            "description": f"{channel_depth} mm deep channel; floor >=5 mm",
            "point": [0, -25, base_thickness - channel_depth],
        },
        "seal_groove": {
            "description": "2 mm wide x 1.4 mm deep rectangular seal recess",
            "point": [0, 32, base_thickness - 1.4],
        },
        "fin_bank": {
            "description": "Nine connected heat-transfer fins; performance unqualified",
            "point": [0, 0, -fin_height],
        },
    }
    cover = Pos(0, 0, base_thickness + 0.15) * Box(
        length, width, cover_thickness, align=cmin
    )
    hole_points = [
        (-length / 2 + 7, -width / 2 + 7),
        (0, -width / 2 + 7),
        (length / 2 - 7, -width / 2 + 7),
        (-length / 2 + 7, 0),
        (length / 2 - 7, 0),
        (-length / 2 + 7, width / 2 - 7),
        (0, width / 2 - 7),
        (length / 2 - 7, width / 2 - 7),
    ]
    flat = Rectangle(length, width)
    from build123d import Circle

    for i, (x, y) in enumerate(hole_points):
        body -= Pos(x, y, base_thickness - 10) * Cylinder(1.65, 11, align=cmin)
        cover -= Pos(x, y, base_thickness) * Cylinder(
            2.05, cover_thickness + 1, align=cmin
        )
        cover -= Pos(x, y, base_thickness + 0.15 + cover_thickness - 2) * Cylinder(
            3.3, 2.2, align=cmin
        )
        flat -= Pos(x, y) * Circle(2.05)
        features[f"cover_bolt_{i + 1}"] = {
            "description": "3.3 mm pilot bore, depth 10 mm; no modeled thread",
            "point": [x, y, base_thickness],
        }
    ports = [(-run / 2 + 4, -25), (-run / 2 + 4, 25)]
    cover_features = {}
    for name, (x, y) in zip(["inlet_port", "outlet_port"], ports):
        cover += Pos(x, y, base_thickness + cover_thickness) * Cylinder(
            7.5, 5, align=cmin
        )
        cover -= Pos(x, y, base_thickness) * Cylinder(
            3.0, cover_thickness + 6, align=cmin
        )
        flat -= Pos(x, y) * Circle(3)
        cover_features[name] = {
            "description": "6 mm plain fluid port aligned to serpentine endpoint",
            "point": [x, y, base_thickness + cover_thickness + 5],
        }
    return Design(
        "cooling_manifold",
        [
            Part("cold_plate", body, "#4FA9BE", features),
            Part("cover", cover, "#D59B58", cover_features),
        ],
        parameters=dict(
            length=length,
            width=width,
            base_thickness=base_thickness,
            channel_width=channel_width,
            channel_depth=channel_depth,
            cover_thickness=cover_thickness,
            fin_height=fin_height,
        ),
        flat_patterns={"cover": flat},
        checks={
            "max_envelope_mm": [200, 160, 100],
            "min_thickness_mm": 3,
            "thicknesses": [
                {
                    "ref": "cold_plate/channel_floor",
                    "mm": base_thickness - channel_depth,
                },
                {"ref": "cover", "mm": cover_thickness},
            ],
        },
    )
