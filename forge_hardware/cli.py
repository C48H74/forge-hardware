import argparse
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(
        prog="forge", description="Local CAD and robot toolkit for coding agents"
    )
    sub = p.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    b.add_argument("source")
    b.add_argument("-o", "--output", default="build/model")
    b.add_argument("--params", default="{}")
    v = sub.add_parser("view")
    v.add_argument("output")
    v.add_argument("--port", type=int, default=8740)
    v.add_argument("--no-browser", action="store_true")
    d = sub.add_parser("daemon")
    d.add_argument("--workspace", default=".")
    d.add_argument("--port", type=int, default=8741)
    m = sub.add_parser("mcp")
    m.add_argument("--workspace", default=".")
    r = sub.add_parser("refs")
    r.add_argument("output")
    c = sub.add_parser("catalog")
    cs = c.add_subparsers(dest="action", required=True)
    u = cs.add_parser("refresh")
    u.add_argument("--repo", default="FreeCAD/FreeCAD-library")
    u.add_argument("--ref", default="master")
    s = cs.add_parser("search")
    s.add_argument("query")
    s.add_argument("--suppliers", action="store_true")
    f = cs.add_parser("download")
    f.add_argument("url")
    f.add_argument("destination")
    f.add_argument("--sha256")
    a = p.parse_args()
    if a.command == "build":
        from .cad.artifacts import build

        print(json.dumps(build(a.source, a.output, json.loads(a.params)), indent=2))
    elif a.command == "view":
        from .viewer.main import serve

        serve(a.output, a.port, not a.no_browser)
    elif a.command == "daemon":
        from .daemon.server import serve

        serve(a.workspace, a.port)
    elif a.command == "mcp":
        from .agent.server import serve

        serve(a.workspace)
    elif a.command == "refs":
        print((Path(a.output) / "refs.json").read_text())
    elif a.command == "catalog":
        from . import catalog

        if a.action == "refresh":
            result = catalog.refresh(repo=a.repo, ref=a.ref)
        elif a.action == "search":
            result = (
                catalog.suppliers(a.query) if a.suppliers else catalog.search(a.query)
            )
        else:
            result = catalog.download(a.url, a.destination, a.sha256)
        print(json.dumps(result, indent=2))
