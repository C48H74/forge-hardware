"""Split bearing housing demonstration, mm; nominal geometry, no fit certification.

Cast/machined aluminium shells, horizontal split through shaft axis. Bearing
counterbores retain nominal 52 mm OD bearings; 30 mm shaft openings. Threads,
bearings and fasteners are omitted. Pins have nominal clearance sockets.
"""

from build123d import Box, Cylinder, Pos, Rot
from forge_hardware.cad.build123d import Design, Part

exploded_display_offsets = {
    "bottom_shell": [0, 0, 0],
    "cover": [0, 0, 55],
    "alignment_pin_left": [0, 0, 22],
    "alignment_pin_right": [0, 0, 22],
}


def build(
    length=180,
    width=80,
    base_height=45,
    cover_height=34,
    wall=7,
    end_wall=14,
    flange_width=14,
    flange_thickness=9,
    bearing_diameter=52,
    bearing_depth=9,
    shaft_diameter=30,
    bolt_diameter=6.6,
    pin_diameter=5,
    seam_clearance=0.15,
):
    vals = locals().copy()
    if min(vals.values()) <= 0:
        raise ValueError("All parameters must be positive")
    if (
        length < 150
        or width < bearing_diameter + 2 * wall
        or base_height < bearing_diameter / 2 + wall
        or cover_height < bearing_diameter / 2 + wall
        or end_wall <= bearing_depth + 3
        or shaft_diameter >= bearing_diameter
        or wall < 5
        or flange_width < 12
        or flange_thickness < 7
        or bolt_diameter > 8
        or pin_diameter > 6
        or seam_clearance > 0.5
    ):
        raise ValueError("Incompatible housing, bearing or flange dimensions")
    split = base_height
    top = split + seam_clearance + cover_height
    fw = width + 2 * flange_width
    # End walls are deliberately thicker than longitudinal walls for bearing seats.
    bottom = Pos(0, 0, split / 2) * Box(length, width, split)
    bottom -= Pos(0, 0, (wall + split + 2) / 2) * Box(
        length - 2 * end_wall, width - 2 * wall, split + 2 - wall
    )
    bottom += Pos(0, 0, split - flange_thickness / 2) * Box(
        length, fw, flange_thickness
    )
    bottom -= Pos(0, 0, split) * Box(
        length - 2 * end_wall, width - 2 * wall, 2 * flange_thickness + 2
    )
    cover = Pos(0, 0, (split + seam_clearance + top) / 2) * Box(
        length, width, cover_height
    )
    cover -= Pos(0, 0, (split + seam_clearance - 2 + top - wall) / 2) * Box(
        length - 2 * end_wall, width - 2 * wall, cover_height - wall + 2
    )
    cover += Pos(0, 0, split + seam_clearance + flange_thickness / 2) * Box(
        length, fw, flange_thickness
    )
    cover -= Pos(0, 0, split + seam_clearance) * Box(
        length - 2 * end_wall, width - 2 * wall, 2 * flange_thickness + 2
    )
    bf = {}
    cf = {}
    # Shaft through-openings and bearing seats machined from the outer end faces.
    through = (
        Pos(0, 0, split) * Rot(0, 90, 0) * Cylinder(shaft_diameter / 2, length + 4)
    )
    bottom -= through
    cover -= through
    for side, sgn in [("left", -1), ("right", 1)]:
        cx = sgn * (length / 2 - bearing_depth / 2)
        seat = (
            Pos(cx, 0, split)
            * Rot(0, 90, 0)
            * Cylinder(bearing_diameter / 2, bearing_depth + 0.02)
        )
        bottom -= seat
        cover -= seat
        f = {
            "point": [sgn * length / 2, 0, split],
            "description": f"{bearing_diameter} mm bearing seat, {bearing_depth} mm depth; split axis",
        }
        bf["bearing_seat_" + side] = f
        cf["bearing_seat_" + side] = dict(f)
    # Integral side ribs merge into the flange and shell wall.
    for i, x in enumerate([-length * 0.34, 0, length * 0.34]):
        for sy in [-1, 1]:
            bottom += Pos(
                x, sy * (width / 2 + flange_width / 2 - 1), split * 0.48
            ) * Box(6, flange_width + 2, split * 0.70)
            cover += Pos(
                x,
                sy * (width / 2 + flange_width / 2 - 1),
                split + seam_clearance + cover_height * 0.54,
            ) * Box(6, flange_width + 2, cover_height * 0.66)
            bf[f"rib_{i}_{'front' if sy < 0 else 'rear'}"] = {
                "point": [x, sy * (fw / 2 - 1), split * 0.48],
                "description": "Integral external reinforcing rib",
            }
    # Four separated mounting feet, accessible vertical clearance holes.
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            x = sx * (length / 2 - 20)
            y = sy * (width / 2 + 12)
            bottom += Pos(x, y, 5) * Box(32, 30, 10)
            bottom -= Pos(x, sy * (width / 2 + 18), 5) * Cylinder(4.5, 14)
            bf[
                f"foot_{'left' if sx < 0 else 'right'}_{'front' if sy < 0 else 'rear'}"
            ] = {
                "point": [x, sy * (width / 2 + 18), 10],
                "description": "9 mm through mounting hole in 10 mm foot",
            }
    # Eight lid bolts, four per long side; no fictitious threads.
    for i, x in enumerate(
        [-length * 0.40, -length * 0.14, length * 0.14, length * 0.40]
    ):
        for sy in [-1, 1]:
            y = sy * (width / 2 + flange_width / 2)
            cutter = Pos(x, y, split) * Cylinder(
                bolt_diameter / 2, 2 * flange_thickness + 5
            )
            bottom -= cutter
            cover -= cutter
            key = f"lid_bolt_{i}_{'front' if sy < 0 else 'rear'}"
            bf[key] = {
                "point": [x, y, split],
                "description": f"{bolt_diameter} mm through clearance hole",
            }
            cf[key] = {
                "point": [x, y, split + seam_clearance],
                "description": f"Matching {bolt_diameter} mm lid clearance hole",
            }
    parts = []
    for label, x, y in [
        ("left", -length * 0.27, -(width / 2 + flange_width / 2)),
        ("right", length * 0.27, width / 2 + flange_width / 2),
    ]:
        bottom -= Pos(x, y, split - 3) * Cylinder(pin_diameter / 2 + 0.025, 6.02)
        cover -= Pos(x, y, split + 3.1) * Cylinder(pin_diameter / 2 + 0.15, 6.4)
        pin = Pos(x, y, split) * Cylinder(pin_diameter / 2, 11.8)
        key = "alignment_" + label
        bf[key] = {
            "point": [x, y, split],
            "description": "Blind nominal dowel socket, 6 mm depth",
        }
        cf[key] = {
            "point": [x, y, split + seam_clearance],
            "description": "Clearance alignment socket",
        }
        parts.append(
            Part(
                "alignment_pin_" + label,
                pin,
                color="#a4aab3",
                features={
                    "axis": {
                        "point": [x, y, split],
                        "description": "Nominal locating dowel axis",
                    }
                },
            )
        )
    bf["split_face"] = {
        "point": [0, width / 2 + flange_width / 2, split],
        "description": "Machined split flange",
    }
    cf["roof"] = {"point": [0, 0, top], "description": f"{wall} mm nominal roof"}
    return Design(
        "gearbox_housing",
        [
            Part("bottom_shell", bottom, color="#397a8b", features=bf),
            Part("cover", cover, color="#8fb8bd", features=cf),
        ]
        + parts,
        parameters=vals,
        checks={
            "min_thickness_mm": 3,
            "thicknesses": [{"ref": "cover/roof", "mm": wall}],
            "max_envelope_mm": [300, 200, 160],
        },
    )
