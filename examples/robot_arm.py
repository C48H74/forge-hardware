"""Two-link arm. Shapes are local mm, joint origin SI, inertia kg m²."""

from build123d import Box, Pos
from forge_hardware.cad.build123d import Design, Part


def box_inertia(m, x, y, z):
    return [
        m * (y * y + z * z) / 12,
        m * (x * x + z * z) / 12,
        m * (x * x + y * y) / 12,
        0,
        0,
        0,
    ]


def build(arm_length=160):
    if arm_length <= 20:
        raise ValueError("arm_length must exceed 20 mm")
    base = Part(
        "base",
        Box(80, 80, 20),
        "#6986e8",
        {"mount": {"point": [0, 0, 10], "description": "Shoulder mounting surface"}},
    )
    arm = Part(
        "arm",
        Pos(arm_length / 2, 0, 0) * Box(arm_length, 24, 20),
        "#e8ad69",
        {
            "tip": {
                "point": [arm_length, 0, 0],
                "description": "End effector mounting point",
            }
        },
    )
    robot = {
        "links": {
            "base": {
                "mass": 0.5,
                "com": [0, 0, 0],
                "inertia": box_inertia(0.5, 0.08, 0.08, 0.02),
            },
            "arm": {
                "mass": 0.2,
                "com": [arm_length / 2000, 0, 0],
                "inertia": box_inertia(0.2, arm_length / 1000, 0.024, 0.02),
            },
        },
        "joints": [
            {
                "name": "shoulder",
                "type": "revolute",
                "parent": "base",
                "child": "arm",
                "xyz": [0, 0, 0.03],
                "rpy": [0, 0, 0],
                "axis": [0, 0, 1],
                "limit": {"lower": -1.57, "upper": 1.57, "effort": 5, "velocity": 1},
            }
        ],
        "groups": {"manipulator": ["shoulder"]},
    }
    return Design(
        "robot_arm", [base, arm], parameters={"arm_length": arm_length}, robot=robot
    )
