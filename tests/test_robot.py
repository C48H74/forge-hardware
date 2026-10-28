import copy
from pathlib import Path
import runpy
import xml.etree.ElementTree as ET
import numpy as np
import pytest
from forge_hardware.robot import validate, zero_transforms
from forge_hardware.cad.artifacts import build

ROOT = Path(__file__).resolve().parents[1]


def robot():
    return runpy.run_path(str(ROOT / "examples/robot_arm.py"))["build"]().robot


def test_robot_exports_and_frames(tmp_path):
    folder = tmp_path / "arm"
    build(ROOT / "examples/robot_arm.py", folder)
    urdf = ET.parse(folder / "robot_arm.urdf").getroot()
    sdf = ET.parse(folder / "robot_arm.sdf").getroot()
    srdf = ET.parse(folder / "robot_arm.srdf").getroot()
    assert urdf.find("joint/origin").attrib["xyz"] == "0.0 0.0 0.03"
    assert urdf.find("link/visual/geometry/mesh").attrib["scale"] == "0.001 0.001 0.001"
    pose = sdf.find("model/link[@name='arm']/pose")
    assert pose.attrib["relative_to"] == "base"
    assert pose.text == "0.0 0.0 0.03 0.0 0.0 0.0"
    assert srdf.find("group/joint").attrib["name"] == "shoulder"
    assert np.allclose(zero_transforms(robot())["arm"][:3, 3], [0, 0, 0.03])
    from build123d import import_step

    combined = import_step(str(folder / "robot_arm.step"))
    assert combined.bounding_box().max.Z == pytest.approx(40)


@pytest.mark.parametrize(
    "mutation", ["mass", "inertia", "cycle", "axis", "limit", "unknown_group"]
)
def test_reject_invalid_robot(mutation):
    r = copy.deepcopy(robot())
    if mutation == "mass":
        r["links"]["arm"]["mass"] = -1
    if mutation == "inertia":
        r["links"]["arm"]["inertia"] = [1, 1, 10, 0, 0, 0]
    if mutation == "cycle":
        r["joints"].append(
            {"name": "loop", "type": "fixed", "parent": "arm", "child": "base"}
        )
    if mutation == "axis":
        r["joints"][0]["axis"] = [0, 0, 0]
    if mutation == "limit":
        r["joints"][0]["limit"]["lower"] = 10
    if mutation == "unknown_group":
        r["groups"]["bad"] = ["missing"]
    with pytest.raises(ValueError):
        validate(r, ["base", "arm"])


def test_external_urdf_parser(tmp_path):
    from urdf_parser_py.urdf import URDF

    folder = tmp_path / "external"
    build(ROOT / "examples/robot_arm.py", folder)
    parsed = URDF.from_xml_file(str(folder / "robot_arm.urdf"))
    assert parsed.get_root() == "base"
    assert parsed.link_map["arm"].inertial.mass == 0.2
    assert parsed.joint_map["shoulder"].limit.effort == 5
    assert parsed.get_chain("base", "arm") == ["base", "shoulder", "arm"]
