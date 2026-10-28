from pathlib import Path
import json
import math
import struct
import zipfile
import pytest
from build123d import import_step
from forge_hardware.cad.artifacts import build

ROOT = Path(__file__).resolve().parents[1]


def test_fixture_exports_and_roundtrip(tmp_path):
    folder = tmp_path / "model"
    manifest = build(ROOT / "examples/fixture.py", folder)
    assert {
        "fixture.step",
        "fixture.stl",
        "fixture.3mf",
        "fixture.glb",
        "flat-base.dxf",
    } <= set(manifest["files"])
    shape = import_step(str(folder / "fixture.step"))
    expected = (90 * 60 - 4 * math.pi * (5.5 / 2) ** 2) * 8
    assert shape.volume == pytest.approx(expected, rel=1e-6)
    assert shape.is_valid
    with zipfile.ZipFile(folder / "fixture.3mf") as z:
        assert any(n.endswith(".model") for n in z.namelist())
    assert (folder / "fixture.glb").read_bytes()[:4] == b"glTF"
    data = (folder / "fixture.stl").read_bytes()
    count = struct.unpack("<I", data[80:84])[0]
    assert len(data) == 84 + count * 50 and count > 12
    import ezdxf

    dxf = ezdxf.readfile(folder / "flat-base.dxf")
    assert len(dxf.modelspace().query("CIRCLE")) == 4
    assert len(dxf.modelspace().query("LINE")) == 4


def test_regeneration_keeps_semantic_ref(tmp_path):
    folder = tmp_path / "model"
    build(ROOT / "examples/fixture.py", folder)
    before = json.loads((folder / "refs.json").read_text())
    build(ROOT / "examples/fixture.py", folder, {"length": 110, "hole_diameter": 6.5})
    after = json.loads((folder / "refs.json").read_text())
    ref = "base/hole_front_left"
    assert ref in before["base"]["features"] and ref in after["base"]["features"]
    assert after["base"]["features"][ref]["point"][0] == -45
    assert after["base"]["volume_mm3"] > before["base"]["volume_mm3"]


def test_failure_preserves_previous_outputs(tmp_path):
    folder = tmp_path / "model"
    build(ROOT / "examples/fixture.py", folder)
    before = (folder / "manifest.json").read_bytes()
    with pytest.raises(ValueError):
        build(ROOT / "examples/fixture.py", folder, {"thickness": -1})
    assert (folder / "manifest.json").read_bytes() == before
    arbitrary = tmp_path / "arbitrary"
    arbitrary.mkdir()
    (arbitrary / "notes.txt").write_text("keep")
    with pytest.raises(ValueError):
        build(ROOT / "examples/fixture.py", arbitrary)
    assert (arbitrary / "notes.txt").read_text() == "keep"
