"""Generate platform manifests from the toolkit's canonical package metadata."""
import argparse
import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def manifests(root=ROOT):
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    identity = {
        "name": project["name"], "version": project["version"],
        "description": project["description"],
        "author": {"name": "C48H74", "url": "https://github.com/C48H74"},
        "repository": "https://github.com/C48H74/forge-hardware",
        "license": "MIT",
    }
    plugin = {**identity, "skills": "./skills/"}
    marketplace = {
        "name": "forge-hardware", "owner": {"name": "C48H74"},
        "plugins": [{"name": project["name"], "source": "./", "version": project["version"],
                     "description": project["description"]}],
    }
    interface = {
        "displayName": "Forge Hardware",
        "shortDescription": "Create editable CAD and robot models",
        "developerName": "C48H74", "category": "Productivity",
        "capabilities": ["Read", "Write"],
        "defaultPrompt": ["Create a 90 × 60 × 8 mm fixture plate with four 5.5 mm holes. Export STEP and show a preview."],
    }
    return {
        "plugin.json": {
            "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            **identity, "extensions": {"com.openai": {"interface": interface}},
        },
        ".claude-plugin/plugin.json": plugin,
        ".claude-plugin/marketplace.json": marketplace,
        ".cursor-plugin/plugin.json": plugin,
        ".cursor-plugin/marketplace.json": marketplace,
        ".codex-plugin/plugin.json": {**plugin, "interface": interface},
        ".agents/plugins/marketplace.json": {
            "name": "forge-hardware", "interface": {"displayName": "Forge Hardware"},
            "plugins": [{"name": project["name"],
                         "source": {"source": "local", "path": "./"},
                         "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                         "category": "Productivity"}],
        },
        "gemini-extension.json": {k: identity[k] for k in ("name", "version", "description")},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if committed manifests are stale")
    args = parser.parse_args()
    stale = []
    for name, data in manifests().items():
        path = ROOT / name
        content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if stale:
        parser.exit(1, "Stale manifests: " + ", ".join(stale) + "\nRun python scripts/build_extensions.py\n")
    print("Extension manifests verified" if args.check else "Extension manifests generated")


if __name__ == "__main__":
    main()
