"""Small, explicit contract between agent-authored Python and the CAD runtime.
CAD dimensions are mm. Robot origins, mass, inertia and joint limits use SI.
"""

from dataclasses import dataclass, field
from typing import Any
import re


def identifier(value):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", value):
        raise ValueError(f"Invalid identifier: {value!r}")
    return value


@dataclass
class Part:
    id: str
    shape: Any
    color: str = "#60b8bf"
    features: dict = field(default_factory=dict)

    # Feature values: {description, point:[x,y,z] in part-local mm}.
    def __post_init__(self):
        identifier(self.id)
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", self.color):
            raise ValueError("Part color must be #RRGGBB")
        for key in self.features:
            identifier(key)


@dataclass
class Design:
    name: str
    parts: list[Part]
    parameters: dict = field(default_factory=dict)
    flat_patterns: dict = field(default_factory=dict)
    robot: dict | None = None
    checks: dict = field(default_factory=dict)

    def __post_init__(self):
        identifier(self.name)
        ids = [p.id for p in self.parts]
        if not ids or len(set(ids)) != len(ids):
            raise ValueError("Design needs uniquely named parts")
        for name in self.flat_patterns:
            identifier(name)
