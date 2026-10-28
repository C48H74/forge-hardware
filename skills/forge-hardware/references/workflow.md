# Modeling contract

The toolkit repository contains `examples/fixture.py`, `examples/bracket.py`, and `examples/robot_arm.py`. Start from the closest example and retain project-local editable source.

```python
from build123d import Box
from forge_hardware.cad.build123d import Design, Part

def build(length=40, width=20, thickness=5):
    if min(length,width,thickness) <= 0:
        raise ValueError('Dimensions must be positive')
    return Design('plate', [Part('base', Box(length,width,thickness),
        features={'top': {'point':[0,0,thickness/2],
                          'description':'Mounting surface'}})],
        parameters=dict(length=length,width=width,thickness=thickness))
```

`Design.flat_patterns` maps names to actual XY sketches/wires. DXF is conditional on an explicit flat pattern; it is not emitted for arbitrary solids. All parts must be valid positive-volume solids. Multiple parts are exported as a compound, not automatically fused.

`Part.features` maps stable semantic names to JSON-compatible dictionaries with `description` and a local `point`. `refs.json` also lists face centers and areas for inspection. The face enumeration can change after any topology edit. Never use it as a persistent topological ID.

## Robot schema

`Design.robot` is a dictionary:

- `links`: map from each Part ID to `{mass, com:[x,y,z], inertia:[ixx,iyy,izz,ixy,ixz,iyz]}`. Inertia is about COM, expressed in an inertia frame aligned with the local link frame. Use physical SI values, never mm-based inertia.
- `joints`: list of `{name,type,parent,child,xyz,rpy,axis,limit}`. `xyz` and fixed-axis XYZ `rpy` locate the child frame relative to the parent at zero joint position. Axis is normalized in the joint frame. Limit is `{lower,upper,effort,velocity}`; continuous joints omit lower and upper, fixed joints omit axis and limit.
- `groups`: map from SRDF group name to joint names. No automatic collision-disable pairs or end effectors are invented.

Supported types: fixed, revolute, continuous, prismatic. Require one tree and one root. Loops, mimic joints, transmissions and controllers require extending the schema first. URDF/SDF reference `meshes/<link>.stl` using scale 0.001 because mesh vertices remain in mm. Keep mesh directory adjacent to XML files. STEP/GLB/3MF assembly exports apply the zero-pose link transforms. Robot collision geometry currently uses the visual mesh; simplify it explicitly for simulation performance.

## Verification and review

Run tests and benchmarks from the repository root. Inspect actual geometry through SVG or the offline canvas viewer. The viewport uses tessellated surfaces and per-pixel depth buffering. Use STEP in a CAD application for final exact geometric review. DFM checks cover envelopes and declared thicknesses only. Engineering SVG projections are review drawings, not automatically toleranced production drawings.
