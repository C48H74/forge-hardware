# Modeling

Use `Design(name, parts, parameters={}, flat_patterns={}, robot=None, checks={})` and `Part(id, shape, color='#60b8bf', features={})` from `forge_hardware.cad.build123d`.

A trusted source must export `build(**parameters) -> Design`. Every part needs a unique filesystem-safe identifier and a valid solid. Parameters reported in `Design.parameters` should include every effective default. JSON overrides are passed as keyword arguments; unsupported names fail instead of being silently ignored.

Features use semantic IDs, descriptions and local-mm points. Example:

```python
Part('base', shape, features={
    'hole_front_left': {'description':'5.5 mm through hole', 'point':[-35,-20,4]}
})
```

The viewer exposes `base/hole_front_left`, and `refs.json` also includes per-face center and area. Face enumeration is build-specific, not persistent naming. A feature point is a reference annotation; it does not constrain geometry automatically. The agent must edit the corresponding source feature.

Explicit XY flat sketches generate SVG and DXF without pretending to unfold arbitrary solids. Account for kerf, tolerances and bend allowances in source if needed. Multiple parts export as a compound; fuse intended monolithic solids explicitly.

## Robots

Each robot link corresponds to one Part ID and a shape expressed in its **local frame** in mm. Robot metadata is SI:

```python
robot = {
  'links': {
    'base': {'mass':0.5, 'com':[0,0,0],
             'inertia':[0.0002,0.0002,0.0002,0,0,0]},
    'arm': {'mass':0.2, 'com':[0.08,0,0],
            'inertia':[0.00002,0.00045,0.00045,0,0,0]}
  },
  'joints': [{'name':'shoulder','type':'revolute',
              'parent':'base','child':'arm','xyz':[0,0,0.03],
              'rpy':[0,0,0],'axis':[0,0,1],
              'limit':{'lower':-1.57,'upper':1.57,'effort':5,'velocity':1}}],
  'groups': {'manipulator':['shoulder']}
}
```

Mass is kg; COM and origin are m; angles are rad; inertia is kg·m² in `[ixx,iyy,izz,ixy,ixz,iyz]` order about COM, aligned with the link frame. Values must be physical; estimate explicitly and label assumptions if manufacturer properties are unknown. The example's numbers illustrate the schema, not a measured product.

URDF origins locate the child/joint frame relative to its parent at zero configuration. SDF link poses use explicit `relative_to` parents and joint poses use the child frame. Axis is normalized in the joint frame. Root is at the model origin. Fixed/revolute/continuous/prismatic joints are supported; continuous joints omit lower/upper limits. Physical inertia validation checks finite values, positive eigenvalues and the principal-moment triangle inequality.

Keep the `meshes/` directory alongside robot XML. URDF/SDF scale local STL meshes by 0.001. CAD assembly exports apply zero-pose transforms. The viewer computes forward kinematics for interactive joint controls. Mesh collisions are visual-mesh proxies; add simplified geometry and simulator-specific metadata before serious simulation.
