"""Validated tree robots: fixed, revolute, continuous and prismatic joints."""

import math
import xml.etree.ElementTree as ET
import numpy as np
from .cad.build123d import identifier


def vector(value, n=3):
    if len(value) != n or not all(math.isfinite(float(x)) for x in value):
        raise ValueError(f"Expected {n} finite values")
    return [float(x) for x in value]


def transform(xyz=(0, 0, 0), rpy=(0, 0, 0)):
    r, p, y = vector(rpy)
    cr, sr, cp, sp, cy, sy = (
        math.cos(r),
        math.sin(r),
        math.cos(p),
        math.sin(p),
        math.cos(y),
        math.sin(y),
    )
    m = np.eye(4)
    m[:3, :3] = [
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr],
    ]
    m[:3, 3] = vector(xyz)
    return m


def validate(robot, part_ids):
    links = robot["links"]
    if set(links) != set(part_ids):
        raise ValueError(
            "Robot links must match part IDs exactly (geometry is link-local)"
        )
    for name, link in links.items():
        identifier(name)
        if not math.isfinite(link["mass"]) or link["mass"] <= 0:
            raise ValueError("Mass must be positive kg")
        vector(link.get("com", [0, 0, 0]))
        a, b, c, d, e, f = vector(link["inertia"], 6)
        eigen = np.linalg.eigvalsh([[a, d, e], [d, b, f], [e, f, c]])
        if min(eigen) <= 0 or eigen[-1] > sum(eigen[:2]) + 1e-12:
            raise ValueError(f"Nonphysical inertia for {name}")
    parents, names = {}, set()
    for j in robot.get("joints", []):
        identifier(j["name"])
        if j["name"] in names or j["name"] in links:
            raise ValueError("Duplicate joint name")
        names.add(j["name"])
        if j["type"] not in {"fixed", "revolute", "continuous", "prismatic"}:
            raise ValueError("Unsupported joint type")
        if j["parent"] not in links or j["child"] not in links or j["child"] in parents:
            raise ValueError("Invalid parent/child or multiple parents")
        parents[j["child"]] = j["parent"]
        vector(j.get("xyz", [0, 0, 0]))
        vector(j.get("rpy", [0, 0, 0]))
        if j["type"] != "fixed":
            axis = vector(j.get("axis", [0, 0, 1]))
            if abs(np.linalg.norm(axis) - 1) > 1e-6:
                raise ValueError("Joint axis must be normalized")
            limit = j["limit"]
            if not all(math.isfinite(float(v)) for v in limit.values()):
                raise ValueError("Nonfinite joint limit")
            if limit["effort"] <= 0 or limit["velocity"] <= 0:
                raise ValueError("Positive effort and velocity required")
            if j["type"] != "continuous" and limit["lower"] > limit["upper"]:
                raise ValueError("Reversed joint limits")
    roots = set(links) - set(parents)
    if len(roots) != 1:
        raise ValueError("Robot must have one root")
    root = roots.pop()
    for name in links:
        seen, current = set(), name
        while current in parents:
            if current in seen:
                raise ValueError("Robot cycle")
            seen.add(current)
            current = parents[current]
        if current != root:
            raise ValueError("Disconnected robot")
    for group, members in robot.get("groups", {}).items():
        identifier(group)
        if not set(members) <= names:
            raise ValueError("SRDF group references unknown joint")
    return root


def zero_transforms(robot):
    root = validate(robot, robot["links"])
    matrices = {root: np.eye(4)}
    pending = list(robot.get("joints", []))
    while pending:
        for joint in pending[:]:
            if joint["parent"] in matrices:
                matrices[joint["child"]] = matrices[joint["parent"]] @ transform(
                    joint.get("xyz", [0, 0, 0]), joint.get("rpy", [0, 0, 0])
                )
                pending.remove(joint)
    return matrices


def text(v):
    return " ".join(str(float(x)) for x in v)


def child(node, tag, content=None, **attrs):
    e = ET.SubElement(node, tag, {k: str(v) for k, v in attrs.items()})
    if content is not None:
        e.text = str(content)
    return e


def save(root, path):
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def export_robot(design, folder):
    robot = design.robot
    validate(robot, [p.id for p in design.parts])
    urdf = ET.Element("robot", name=design.name)
    srdf = ET.Element("robot", name=design.name)
    sdf = ET.Element("sdf", version="1.9")
    model = child(sdf, "model", name=design.name)
    by_child = {j["child"]: j for j in robot.get("joints", [])}
    for name, data in robot["links"].items():
        link = child(urdf, "link", name=name)
        inertial = child(link, "inertial")
        child(inertial, "origin", xyz=text(data.get("com", [0, 0, 0])), rpy="0 0 0")
        child(inertial, "mass", value=data["mass"])
        keys = ["ixx", "iyy", "izz", "ixy", "ixz", "iyz"]
        child(inertial, "inertia", **dict(zip(keys, data["inertia"])))
        slink = child(model, "link", name=name)
        joint = by_child.get(name)
        pose = (
            text(joint.get("xyz", [0, 0, 0]) + joint.get("rpy", [0, 0, 0]))
            if joint
            else "0 0 0 0 0 0"
        )
        child(
            slink, "pose", pose, relative_to=joint["parent"] if joint else "__model__"
        )
        si = child(slink, "inertial")
        child(si, "pose", text(data.get("com", [0, 0, 0])) + " 0 0 0")
        child(si, "mass", data["mass"])
        tensor = child(si, "inertia")
        for k, v in zip(keys, data["inertia"]):
            child(tensor, k, v)
        for kind in ["visual", "collision"]:
            geom = child(child(link, kind), "geometry")
            child(
                geom, "mesh", filename=f"meshes/{name}.stl", scale="0.001 0.001 0.001"
            )
            sg = child(child(slink, kind, name=kind), "geometry")
            sm = child(sg, "mesh")
            child(sm, "uri", f"meshes/{name}.stl")
            child(sm, "scale", "0.001 0.001 0.001")
    for j in robot.get("joints", []):
        uj = child(urdf, "joint", name=j["name"], type=j["type"])
        child(uj, "parent", link=j["parent"])
        child(uj, "child", link=j["child"])
        child(
            uj,
            "origin",
            xyz=text(j.get("xyz", [0, 0, 0])),
            rpy=text(j.get("rpy", [0, 0, 0])),
        )
        sj = child(
            model,
            "joint",
            name=j["name"],
            type="revolute" if j["type"] == "continuous" else j["type"],
        )
        child(sj, "parent", j["parent"])
        child(sj, "child", j["child"])
        child(sj, "pose", "0 0 0 0 0 0", relative_to=j["child"])
        if j["type"] != "fixed":
            child(uj, "axis", xyz=text(j.get("axis", [0, 0, 1])))
            limits = {
                k: v
                for k, v in j["limit"].items()
                if k in {"effort", "velocity", "lower", "upper"}
            }
            if j["type"] == "continuous":
                limits = {
                    k: v for k, v in limits.items() if k in {"effort", "velocity"}
                }
            child(uj, "limit", **limits)
            sa = child(sj, "axis")
            child(sa, "xyz", text(j.get("axis", [0, 0, 1])))
            lim = child(sa, "limit")
            for k, v in limits.items():
                child(lim, k, v)
    for name, joints in robot.get("groups", {}).items():
        group = child(srdf, "group", name=name)
        for j in joints:
            child(group, "joint", name=j)
    save(urdf, folder / f"{design.name}.urdf")
    save(srdf, folder / f"{design.name}.srdf")
    save(sdf, folder / f"{design.name}.sdf")
