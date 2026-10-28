"""Artifact generation, semantic references and atomic build publication."""

from pathlib import Path
import hashlib
import json
import runpy
import sys
import shutil
import tempfile
import time
import numpy as np
from build123d import (
    Compound,
    Color,
    ExportDXF,
    ExportSVG,
    Mesher,
    export_step,
    export_stl,
    export_gltf,
)
from .build123d import Design
from ..viewer.tessellation import mesh, review_image
from ..robot import export_robot, zero_transforms
from ..capabilities import dfm, fabrication


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(source, output, parameters=None):
    source, output = Path(source).resolve(), Path(output).resolve()
    if output == source.parent or output in source.parents:
        raise ValueError("Output must not contain source")
    started = time.perf_counter()
    sys.path.insert(0, str(source.parent))
    try:
        module = runpy.run_path(str(source))  # trusted local Python only
    finally:
        sys.path.pop(0)
    design = module["build"](**(parameters or {}))
    if not isinstance(design, Design):
        raise TypeError("build(**parameters) must return Design")
    transforms = zero_transforms(design.robot) if design.robot else {}
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".forge-", dir=output.parent))
    try:
        (stage / "meshes").mkdir()
        scene = {
            "name": design.name,
            "units": "mm",
            "parts": [],
            "robot": design.robot,
            "parameters": design.parameters,
        }
        refs = {}
        shapes = []
        for part in design.parts:
            if not part.shape.is_valid or part.shape.volume <= 0:
                raise ValueError(f"Invalid or non-solid part: {part.id}")
            local = part.shape
            local.label = part.id
            local.color = Color(part.color)
            matrix = transforms.get(part.id, np.eye(4))
            # STEP/GLB/3MF assembly at zero configuration; STL per link stays local.
            from OCP.gp import gp_Trsf

            tr = gp_Trsf()
            m = matrix.copy()
            m[:3, 3] *= 1000
            tr.SetValues(*m[:3, :].flatten().tolist())
            from build123d import Matrix

            placed = local.transform_shape(Matrix(tr))
            placed.label = part.id
            shapes.append(placed)
            export_stl(local, str(stage / "meshes" / f"{part.id}.stl"), tolerance=0.1)
            data = mesh(local)
            vertices = np.array(data["vertices"])
            world = vertices @ matrix[:3, :3].T + matrix[:3, 3] * 1000
            scene["parts"].append(
                {
                    "id": part.id,
                    "color": part.color,
                    **data,
                    "review_vertices": world.tolist(),
                    "features": part.features,
                }
            )
            faces = []
            for i, face in enumerate(local.faces()):
                faces.append(
                    {
                        "ref": f"{part.id}/face/{i}",
                        "center_mm": list(face.center()),
                        "area_mm2": face.area,
                    }
                )
            refs[part.id] = {
                "features": {f"{part.id}/{k}": v for k, v in part.features.items()},
                "faces": faces,
                "volume_mm3": local.volume,
                "bounds_mm": list(local.bounding_box().size),
            }
        assembly = Compound(children=shapes)
        for extension, exporter in [("step", export_step), ("stl", export_stl)]:
            if not exporter(assembly, str(stage / f"{design.name}.{extension}")):
                raise RuntimeError(f"{extension} export failed")
        if not export_gltf(assembly, str(stage / f"{design.name}.glb"), binary=True):
            raise RuntimeError("GLB export failed")
        mesher = Mesher()
        mesher.add_shape(assembly)
        mesher.write(str(stage / f"{design.name}.3mf"))
        for name, flat in design.flat_patterns.items():
            # Explicit XY manufacturing geometry, never an inferred unfold.
            for cls, ext in [(ExportDXF, "dxf"), (ExportSVG, "svg")]:
                exp = cls()
                exp.add_shape(flat)
                exp.write(str(stage / f"flat-{name}.{ext}"))
        visible, _ = assembly.project_to_viewport((150, -200, 170))
        svg = ExportSVG()
        svg.add_shape(visible)
        svg.write(str(stage / "drawing-isometric.svg"))
        for name, origin, up in [
            ("top", (0, 0, 1000), (0, 1, 0)),
            ("front", (0, -1000, 0), (0, 0, 1)),
            ("right", (1000, 0, 0), (0, 0, 1)),
        ]:
            edges, _ = assembly.project_to_viewport(origin, viewport_up=up)
            drawing = ExportSVG()
            drawing.add_shape(edges)
            drawing.write(str(stage / f"drawing-{name}.svg"))
        (stage / "dimensions.json").write_text(
            json.dumps(
                {
                    "units": "mm",
                    "overall_envelope": list(assembly.bounding_box().size),
                    "note": "Envelope dimensions only; add manufacturing dimensions and tolerances in source/drawing workflow.",
                },
                indent=2,
            )
        )
        review_image(scene, stage / "review.svg")
        # Local render data includes zero-pose transforms separately for runtime FK.
        for p in scene["parts"]:
            p.pop("review_vertices", None)
        (stage / "scene.json").write_text(json.dumps(scene))
        (stage / "refs.json").write_text(json.dumps(refs, indent=2))
        (stage / "dfm.json").write_text(json.dumps(dfm(design), indent=2))
        (stage / "fabrication.json").write_text(
            json.dumps(fabrication(design.name), indent=2)
        )
        if design.robot:
            export_robot(design, stage)
        manifest = {
            "schema": 1,
            "design": design.name,
            "source": str(source),
            "source_sha256": digest(source),
            "parameters": parameters or {},
            "resolved_parameters": design.parameters,
            "duration_seconds": round(time.perf_counter() - started, 3),
            "files": {
                str(p.relative_to(stage)): digest(p)
                for p in stage.rglob("*")
                if p.is_file()
            },
            "preview": "review.svg",
            "viewer": "/",
        }
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2))
        # Do not replace arbitrary directories. Old outputs remain if build fails.
        if output.exists():
            if not (output / "manifest.json").is_file():
                raise ValueError("Refusing to replace directory without Forge manifest")
            backup = output.with_name(output.name + ".previous")
            if backup.exists():
                raise ValueError(f"Backup exists: {backup}; move it before rebuilding")
            output.rename(backup)
            try:
                stage.rename(output)
            except BaseException:
                backup.rename(output)
                raise
            shutil.rmtree(backup)
        else:
            stage.rename(output)
        return manifest
    finally:
        if stage.exists():
            shutil.rmtree(stage)
