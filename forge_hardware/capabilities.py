"""Bounded DFM screening and explicit fabrication handoff."""


def dfm(design):
    findings = []
    envelope = design.checks.get("max_envelope_mm")
    for p in design.parts:
        size = list(p.shape.bounding_box().size)
        if envelope and any(a > b for a, b in zip(size, envelope)):
            findings.append(
                {"part": p.id, "check": "envelope", "status": "fail", "size_mm": size}
            )
    for feature in design.checks.get("thicknesses", []):
        minimum = design.checks.get("min_thickness_mm", 1)
        findings.append(
            {
                **feature,
                "check": "declared_thickness",
                "status": "pass" if feature["mm"] >= minimum else "fail",
            }
        )
    return {
        "scope": "Envelope and author-declared thickness screening only; no automatic wall analysis, stress or collision certification.",
        "findings": findings,
    }


def fabrication(design_name):
    return {
        "design": design_name,
        "action": "manual_upload_required",
        "services": [
            {"name": "Xometry", "url": "https://www.xometry.com/"},
            {"name": "PCBWay", "url": "https://www.pcbway.com/"},
            {"name": "JLC3DP", "url": "https://jlc3dp.com/"},
        ],
        "note": "Review material, tolerances and vendor terms before uploading. No files or orders are sent.",
    }
