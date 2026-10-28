"""Real geometry and regeneration checks for the three public showcase models."""

from pathlib import Path
import runpy
import xml.etree.ElementTree as ET
import pytest
from build123d import import_step
from forge_hardware.cad.artifacts import build

ROOT = Path(__file__).resolve().parents[1]
CASES = [("gearbox_housing", 4), ("parallel_gripper", 9), ("cooling_manifold", 2)]


@pytest.fixture(scope="module", params=CASES, ids=[c[0] for c in CASES])
def model(request, tmp_path_factory):
    name, solids = request.param
    folder = tmp_path_factory.mktemp(name) / "model"
    source = ROOT / "examples" / f"{name}.py"
    d = runpy.run_path(str(source))["build"]()
    manifest = build(source, folder)
    return name, solids, d, folder, manifest


def test_showcase_real_roundtrip(model):
    name, count, d, folder, manifest = model
    assert all(p.shape.is_valid and len(p.shape.solids()) == 1 for p in d.parts)
    exported = import_step(str(folder / f"{name}.step"))
    assert exported.is_valid and len(exported.solids()) == count
    assert exported.volume == pytest.approx(
        sum(p.shape.volume for p in d.parts), rel=1e-6
    )
    assert {f"{name}.{ext}" for ext in ["step", "stl", "3mf", "glb"]} <= manifest[
        "files"
    ].keys()
    assert (folder / "review.png").stat().st_size > 1000
    assert all(p.features for p in d.parts)


def test_showcase_reject_invalid_parameters(model):
    name, _, _, _, _ = model
    bad = {
        "gearbox_housing": {"wall": 1},
        "parallel_gripper": {"finger_length": 5},
        "cooling_manifold": {"channel_depth": 50},
    }
    with pytest.raises(ValueError):
        runpy.run_path(str(ROOT / "examples" / f"{name}.py"))["build"](**bad[name])


def test_showcase_targeted_parameter_edits():
    get = lambda name: runpy.run_path(str(ROOT / "examples" / f"{name}.py"))["build"]
    a = get("cooling_manifold")()
    b = get("cooling_manifold")(channel_depth=9)
    assert b.parts[0].shape.volume < a.parts[0].shape.volume
    assert b.parts[1].shape.volume == pytest.approx(a.parts[1].shape.volume)
    assert b.parts[0].features["channel_floor"]["point"][2] == 9
    a = get("parallel_gripper")()
    b = get("parallel_gripper")(finger_length=65)
    for before, after in zip(a.parts, b.parts):
        if before.id.startswith("finger_"):
            assert after.features["tip"]["point"][2] == 65
        else:
            assert after.shape.volume == pytest.approx(before.shape.volume)
    a = get("gearbox_housing")()
    b = get("gearbox_housing")(width=90)
    assert b.parts[0].features["lid_bolt_0_front"]["point"][1] == -52
    assert b.parts[0].shape.volume > a.parts[0].shape.volume


def test_showcase_robot_xml(tmp_path):
    from urdf_parser_py.urdf import URDF

    folder = tmp_path / "robot"
    build(ROOT / "examples/parallel_gripper.py", folder)
    robot = URDF.from_xml_file(str(folder / "parallel_gripper.urdf"))
    assert (
        robot.get_root() == "palm" and len(robot.links) == 9 and len(robot.joints) == 8
    )
    moving = [j for j in robot.joints if j.type == "prismatic"]
    assert len(moving) == 2
    assert {tuple(j.axis) for j in moving} == {(-1.0, 0.0, 0.0), (1.0, 0.0, 0.0)}
    assert all(j.limit.upper == 0.02 for j in moving)
    for ext in ["srdf", "sdf"]:
        ET.parse(folder / f"parallel_gripper.{ext}")
