"""A 90 x 60 x 8 mm fixture with four mounting holes and an XY cutting profile."""

from build123d import Box, Cylinder, Pos, Rectangle, Circle
from forge_hardware.cad.build123d import Design, Part


def build(length=90, width=60, thickness=8, hole_diameter=5.5, inset=10):
    if min(
        length, width, thickness, hole_diameter, inset
    ) <= 0 or 2 * inset + hole_diameter >= min(length, width):
        raise ValueError("Invalid fixture dimensions")
    shape = Box(length, width, thickness)
    flat = Rectangle(length, width)
    features = {}
    for label, x, y in [
        ("front_left", -1, -1),
        ("front_right", 1, -1),
        ("rear_left", -1, 1),
        ("rear_right", 1, 1),
    ]:
        px, py = x * (length / 2 - inset), y * (width / 2 - inset)
        shape -= Pos(px, py, 0) * Cylinder(hole_diameter / 2, thickness + 2)
        flat -= Pos(px, py) * Circle(hole_diameter / 2)
        features[f"hole_{label}"] = {
            "description": f"{hole_diameter} mm through hole",
            "point": [px, py, thickness / 2],
        }
    features["top"] = {
        "description": "Top mounting surface",
        "point": [0, 0, thickness / 2],
    }
    return Design(
        "fixture",
        [Part("base", shape, features=features)],
        parameters=dict(
            length=length,
            width=width,
            thickness=thickness,
            hole_diameter=hole_diameter,
            inset=inset,
        ),
        flat_patterns={"base": flat},
        checks={
            "max_envelope_mm": [200, 200, 200],
            "min_thickness_mm": 2,
            "thicknesses": [{"ref": "base/top", "mm": thickness}],
        },
    )
