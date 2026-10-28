"""Parametric parallel gripper concept, mm CAD and SI robot metadata.
Assumptions: 112 x 64 mm aluminum palm, two independent 20 mm outward
slides, aluminum carriages/fingers, steel guide bars, elastomer grip pads.
No motor, bearings, fasteners, synchronization, tolerances or load rating is
represented. Density-based uniform-solid mass/inertia are estimates; no
controller, collision, manufacturing or simulation validation is claimed.
"""

from build123d import Box, Cylinder, Pos, Rot, CenterOf
from forge_hardware.cad.build123d import Design, Part

exploded_display_offsets = {
    "palm": [0, 0, -20],
    "guide_front": [0, -15, -5],
    "guide_rear": [0, 15, -5],
    "carriage_left": [-20, 0, 8],
    "carriage_right": [20, 0, 8],
    "finger_left": [-30, 0, 20],
    "finger_right": [30, 0, 20],
    "pad_left": [-20, -30, 20],
    "pad_right": [20, 30, 20],
}


def feat(p, text):
    return {"point": p, "description": text}


def physical(shape, density):
    # build123d inertia is unit-density mm^5; kg/mm^3 and mm^2->m^2.
    c = shape.center(CenterOf.MASS)
    a = shape.matrix_of_inertia
    k = density * 1e-15  # density kg/m^3 times mm^5 -> kg m^2
    return {
        "mass": shape.volume * density * 1e-9,
        "com": [c.X / 1000, c.Y / 1000, c.Z / 1000],
        "inertia": [
            a[0][0] * k,
            a[1][1] * k,
            a[2][2] * k,
            a[0][1] * k,
            a[0][2] * k,
            a[1][2] * k,
        ],
    }


def build(finger_length=50, jaw_spacing=50, stroke=20):
    if not 40 <= finger_length <= 80:
        raise ValueError("finger_length must be 40..80 mm")
    if not 44 <= jaw_spacing <= 56 or not 5 <= stroke <= 20:
        raise ValueError("jaw_spacing must be 44..56 mm and stroke 5..20 mm")
    parts = []
    links = {}
    joints = []

    def add(name, shape, color, features, rho=2700):
        if not shape.is_valid or len(shape.solids()) != 1:
            raise ValueError(f"{name} must be one valid connected solid")
        parts.append(Part(name, shape, color, features))
        links[name] = physical(shape, rho)

    def fixed(name, parent, child, xyz):
        joints.append(
            dict(
                name=name,
                type="fixed",
                parent=parent,
                child=child,
                xyz=[v / 1000 for v in xyz],
                rpy=[0, 0, 0],
            )
        )

    palm = Box(112, 64, 20)
    for x in (-43, 43):
        for y in (-24, 24):
            palm -= Pos(x, y, 0) * Cylinder(2.75, 24)
            palm -= Pos(x, y, 8) * Cylinder(4.75, 5)
    # Two shallow milled rail seats and a central recessed service pocket.
    for y in (-16, 16):
        palm -= Pos(0, y, 9) * Box(100, 8.2, 4)
    palm -= Pos(0, 0, 8) * Box(76, 16, 6)
    add(
        "palm",
        palm,
        "#50677f",
        {
            "robot_mount": feat(
                [0, 0, -10], "Wrist interface; four M5 clearance holes"
            ),
            "mount_front_left": feat(
                [-43, -24, 0], "5.5 mm through bore with counterbore"
            ),
            "service_pocket": feat([0, 0, 5], "Milled central service recess"),
            "rail_seat_front": feat([0, -16, 7], "Front guide seat floor"),
        },
    )
    for name, y in [("guide_front", -16), ("guide_rear", 16)]:
        rail = Box(104, 8, 8)
        for x in (-47, 47):
            rail -= Pos(x, 0, 0) * Cylinder(1.7, 12)
        add(
            name,
            rail,
            "#b1bcc6",
            {"slide_axis": feat([0, 0, 4], "X-axis linear guide running surface")},
            7850,
        )
        fixed(name + "_mount", "palm", name, [0, y, 11])
    for side, sign in [("left", -1), ("right", 1)]:
        car = Box(18, 42, 14)
        for y in (-16, 16):
            car -= Pos(0, y, -5) * Box(22, 8.6, 6)
        for y in (-6, 6):
            car -= Pos(0, y, 0) * Cylinder(1.7, 18)
        cname = "carriage_" + side
        add(
            cname,
            car,
            "#ed9c42",
            {
                "finger_mount": feat([0, 0, 7], "Two M3 clearance bores"),
                "guide_channel_front": feat(
                    [0, -16, -2], "8.6 mm guide clearance channel"
                ),
            },
        )
        joints.append(
            dict(
                name="slide_" + side,
                type="prismatic",
                parent="palm",
                child=cname,
                xyz=[sign * jaw_spacing / 2000, 0, 0.022],
                rpy=[0, 0, 0],
                axis=[sign, 0, 0],
                limit=dict(lower=0, upper=stroke / 1000, effort=40, velocity=0.05),
            )
        )
        # Tall fingers: blind lightening recess on outer face, cross-drilled bores.
        f = Pos(0, 0, finger_length / 2) * Box(12, 18, finger_length)
        f -= Pos(sign * 4.5, 0, finger_length * 0.55) * Box(6, 11, finger_length - 20)
        for z in (8, finger_length - 8):
            f -= Pos(0, 0, z) * Rot(0, 90, 0) * Cylinder(2, 18)
        fname = "finger_" + side
        add(
            fname,
            f,
            "#ccd5df",
            {
                "tip": feat([0, 0, finger_length], "Finger tip"),
                "outer_pocket": feat(
                    [sign * 6, 0, finger_length * 0.55], "Blind weight-reduction pocket"
                ),
                "upper_cross_bore": feat(
                    [0, 0, finger_length - 8], "4 mm transverse bore"
                ),
                "grip_face": feat(
                    [-sign * 6, 0, finger_length - 12], "Pad attachment face"
                ),
            },
        )
        fixed(fname + "_mount", cname, fname, [0, 0, 7])
        pad = Box(3, 17, 22)
        # Shallow horizontal serrations in inward contact face.
        for z in (-8, -4, 0, 4, 8):
            pad -= Pos(-sign * 1.3, 0, z) * Box(0.8, 19, 0.8)
        pname = "pad_" + side
        add(
            pname,
            pad,
            "#253339",
            {
                "contact_face": feat(
                    [-sign * 1.5, 0, 0], "Serrated elastomer grip surface"
                )
            },
            1100,
        )
        fixed(pname + "_mount", fname, pname, [-sign * 7.5, 0, finger_length - 12])
    return Design(
        "parallel_gripper",
        parts,
        parameters=dict(
            finger_length=finger_length, jaw_spacing=jaw_spacing, stroke=stroke
        ),
        robot=dict(
            links=links,
            joints=joints,
            groups={"gripper": ["slide_left", "slide_right"]},
        ),
    )
