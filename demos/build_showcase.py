"""Regenerate three complex demonstrations, parameter variants, and evidence.
Run: python demos/build_showcase.py [--render]
"""

from pathlib import Path
import argparse
import hashlib
import json
import runpy
from build123d import import_step
from forge_hardware.cad.artifacts import build

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("gearbox_housing", 4, {"width": 90}),
    ("parallel_gripper", 9, {"finger_length": 65}),
    ("cooling_manifold", 2, {"channel_depth": 9}),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    report = {
        "schema": 1,
        "scope": "Nominal geometry, actual file roundtrips and parameter regeneration. No manufacturing, pressure, thermal, load or simulator certification.",
        "models": [],
    }
    for name, count, edit in CASES:
        source = ROOT / "examples" / f"{name}.py"
        folder = ROOT / "build" / name
        manifest = build(source, folder)
        original = runpy.run_path(str(source))["build"]()
        reopened = import_step(str(folder / f"{name}.step"))
        assert reopened.is_valid and len(reopened.solids()) == count
        total = sum(p.shape.volume for p in original.parts)
        assert abs(reopened.volume - total) < max(1e-4, total * 1e-6)
        row = {
            "model": name,
            "source": str(source.relative_to(ROOT)),
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "parts": len(original.parts),
            "valid_solids": len(reopened.solids()),
            "step_roundtrip_valid": reopened.is_valid,
            "volume_mm3": round(reopened.volume, 6),
            "envelope_mm": list(reopened.bounding_box().size),
            "semantic_features": sum(len(p.features) for p in original.parts),
            "build_seconds": manifest["duration_seconds"],
            "exports": {
                k: v
                for k, v in manifest["files"].items()
                if k.endswith(
                    (".step", ".stl", ".3mf", ".glb", ".dxf", ".urdf", ".srdf", ".sdf")
                )
            },
        }
        edited = ROOT / "build" / "showcase_edits" / name
        build(source, edited, edit)
        edited_step = import_step(str(edited / f"{name}.step"))
        assert edited_step.is_valid and len(edited_step.solids()) == count
        after = runpy.run_path(str(source))["build"](**edit)
        unchanged = [
            a.id
            for a, b in zip(original.parts, after.parts)
            if abs(a.shape.volume - b.shape.volume) < 1e-6 and a.features == b.features
        ]
        row["parameter_edit"] = {
            "parameters": edit,
            "step_roundtrip_valid": edited_step.is_valid,
            "volume_mm3": round(edited_step.volume, 6),
            "unchanged_parts": unchanged,
        }
        if name == "parallel_gripper":
            from urdf_parser_py.urdf import URDF

            robot = URDF.from_xml_file(str(folder / f"{name}.urdf"))
            row["robot"] = {
                "parser": "urdf_parser_py",
                "root": robot.get_root(),
                "links": len(robot.links),
                "joints": len(robot.joints),
                "moving_joints": 2,
                "mass_properties": "Uniform-solid estimates from assumed material densities; not measured.",
            }
        report["models"].append(row)
        print(name, ":", count, "valid STEP solids; edit verified", flush=True)
    (ROOT / "demos" / "verification.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    if args.render:
        runpy.run_path(str(ROOT / "demos" / "render_gallery.py"), run_name="__main__")


if __name__ == "__main__":
    main()
