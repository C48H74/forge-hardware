"""Union of two intersecting plates; semantic references survive parameter edits."""

from build123d import Box, Pos, Cylinder
from forge_hardware.cad.build123d import Design, Part


def build(width=50, height=50, thickness=5):
    if min(width, height, thickness) <= 0 or thickness >= min(width, height):
        raise ValueError("Invalid bracket")
    shape = Box(width, width, thickness) + Pos(
        0, width / 2 - thickness / 2, height / 2 - thickness / 2
    ) * Box(width, thickness, height)
    shape -= Pos(0, -10, 0) * Cylinder(3, thickness + 2)
    return Design(
        "bracket",
        [
            Part(
                "bracket",
                shape,
                features={
                    "mount_hole": {
                        "point": [0, -10, thickness / 2],
                        "description": "6 mm base through hole",
                    }
                },
            )
        ],
        parameters={"width": width, "height": height, "thickness": thickness},
    )
