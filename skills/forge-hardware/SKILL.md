---
name: forge-hardware
description: Turn plain-language hardware ideas into editable parametric CAD and robot design files using the Forge Hardware toolkit. Use for parts, fixtures, mechanisms, assemblies, STEP components, STEP/STL/3MF/DXF/GLB exports, URDF/SRDF/SDF robots, local geometry previews, and precise follow-up edits using semantic model references.
---

# Forge Hardware

Use the agent as the language-to-source translator. Keep geometry in editable Python; regenerate outputs with the toolkit. Do not claim a standalone natural-language model or automatic engineering certification.

## Languages

Keep English as the canonical language. Read [Português](references/pt-BR.md) or [Español](references/es.md) when requested. Match the user’s response language while preserving commands and model identifiers. The local viewer offers English, Portuguese and Spanish.

## Set up

Read [workflow.md](references/workflow.md) for the source contract, units and robot conventions. Locate an existing Forge Hardware checkout first. If absent, clone `https://github.com/C48H74/forge-hardware.git` into the user's project tools directory. Create a Python 3.11–3.13 virtual environment and run `python -m pip install -e /absolute/path/to/forge-hardware` inside it. Use that environment's Python for every command. Never overwrite the user's existing checkout or unrelated files.

## Create

1. Translate the request into requirements: units, dimensions, mounting interfaces, materials, clearances, loads if supplied, and requested exports. Ask only for dimensions or constraints that materially change the result. Record explicit assumptions in the project notes.
2. Write a project-local Python source with `build(**parameters) -> Design`, using `forge_hardware.cad.build123d.Design` and `Part`. Use build123d's real modeling API. Keep parameter names explicit and reject invalid combinations.
3. Name parts and semantic features (`base/hole_front_left`, `arm/tip`). Store feature points in part-local mm. Use geometric selectors for source edits, not saved face indices. Face indices in `refs.json` identify only one build.
4. Model flat patterns explicitly in XY. Do not label a projected silhouette an unfolded sheet-metal pattern. Account for bend allowance in authored geometry when needed.
5. Run `python -m forge_hardware build source.py -o build/design --params '{"length":110}'`. Inspect errors, STEP roundtrip and `refs.json` dimensions/volume. Never silently replace a failed format with a different format.
6. Inspect `review.svg` and launch `python -m forge_hardware view build/design`. Open the local URL where the viewer is running. If your environment cannot open it, provide the launch command and review image without claiming visual verification.
7. Deliver the source, exported files, preview and reproduction command. Report limitations and unverified assumptions relevant to the requested design.

## Edit and regenerate

Resolve user references against `refs.json` and the source. Confirm the semantic feature exists; explain ambiguity if it does not. Change named parameters or the feature construction in source, then regenerate into the same managed output folder. Preserve semantic names when their meaning stays the same. Compare dimensions, volume, feature points and review images to catch unintended changes.

## Use purchased components

Run `python -m forge_hardware catalog search '608 bearing'`. Use `catalog search 'M3 screw' --suppliers` when inventory has no suitable part. Supplier links are searches, not proof of stock, dimensions or license. Download a verified direct STEP URL with `catalog download URL assets/part.step`; retain its `.step.json` provenance. Inspect the STEP geometry and manufacturer dimensions before assembly. Import it with `forge_hardware.cad.step.load_part`. Never execute downloaded code or bypass vendor sign-in/licensing.

## Create robots

Use local link geometry in mm and robot metadata in SI: meters, radians, kilograms and kg·m². Supply explicit physical mass, COM and inertia; label estimates. Read [workflow.md](references/workflow.md) before exporting. Verify one connected acyclic tree, axes, limits and zero-pose transforms. Inspect local viewer joint sliders. URDF/SRDF/SDF output is an interchange starting point: do not claim Gazebo, MoveIt, collision or controller validation unless those checks actually ran.

## Agent interface

Prefer CLI tools when available. For a host with legacy MCP stdio support, run `python -m forge_hardware mcp --workspace /absolute/project`. Tools: `build_design`, `inspect_design`, `preview_design`, `search_parts`, `download_part`. Do not add or configure an MCP connection without the host's applicable server review. Builds execute trusted local Python; the daemon is not a sandbox.

For the optional token-protected local build daemon and same-origin React embedding, read the toolkit's `docs/architecture.md`. Keep viewer serving read-only on loopback. Never upload a design to fabrication services or order manufacturing unless the user requests that action.
