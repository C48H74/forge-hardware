"""MCP stdio tools. JSON-RPC newline framing; no network listener."""

from pathlib import Path
import json
import subprocess
import sys


def tools():
    def tool(name, description, properties, required):
        return {
            "name": name,
            "description": description,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        }

    string = {"type": "string"}
    return [
        tool(
            "build_design",
            "Execute trusted local parametric source and regenerate CAD/robot outputs.",
            {"source": string, "output": string, "parameters": {"type": "object"}},
            ["source", "output"],
        ),
        tool(
            "inspect_design",
            "Read manifest, semantic references and DFM report.",
            {"output": string},
            ["output"],
        ),
        tool(
            "preview_design",
            "Return local preview asset paths and viewer launch command.",
            {"output": string},
            ["output"],
        ),
        tool(
            "search_parts",
            "Search cached public STEP inventory or supplier search links.",
            {"query": string, "suppliers": {"type": "boolean"}},
            ["query"],
        ),
        tool(
            "download_part",
            "Download public STEP with provenance; never execute it.",
            {"url": string, "destination": string, "sha256": string},
            ["url", "destination"],
        ),
    ]


def serve(workspace):
    workspace = Path(workspace).resolve()

    def local(value):
        path = (workspace / value).resolve()
        if not path.is_relative_to(workspace):
            raise ValueError("Path outside workspace")
        return path

    def call(name, args):
        from .. import catalog

        if name == "build_design":
            source, output = local(args["source"]), local(args["output"])
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "forge_hardware",
                    "build",
                    str(source),
                    "-o",
                    str(output),
                    "--params",
                    json.dumps(args.get("parameters", {})),
                ],
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode:
                raise RuntimeError(result.stderr[-8000:])
            return {"stdout": result.stdout, "output": str(output)}
        if name in {"inspect_design", "preview_design"}:
            folder = local(args["output"])
            if name == "inspect_design":
                return {
                    n: json.loads((folder / f"{n}.json").read_text())
                    for n in ["manifest", "refs", "dfm"]
                }
            return {
                "preview": str(folder / "review.svg"),
                "command": [
                    sys.executable,
                    "-m",
                    "forge_hardware",
                    "view",
                    str(folder),
                ],
                "url": "http://127.0.0.1:8740",
                "note": "Launch the command locally before opening the URL.",
            }
        if name == "search_parts":
            return (
                catalog.suppliers(args["query"])
                if args.get("suppliers")
                else catalog.search(args["query"])
            )
        if name == "download_part":
            return catalog.download(
                args["url"], local(args["destination"]), args.get("sha256")
            )
        raise ValueError("Unknown tool")

    for line in sys.stdin:
        request = None
        try:
            request = json.loads(line)
            method = request.get("method")
            if "id" not in request:
                continue
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "forge-hardware", "version": "0.1.0"},
                }
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": tools()}
            elif method == "tools/call":
                try:
                    params = request["params"]
                    value = call(params["name"], params.get("arguments", {}))
                    result = {
                        "content": [{"type": "text", "text": json.dumps(value)}],
                        "isError": False,
                    }
                except Exception as e:
                    result = {
                        "content": [{"type": "text", "text": str(e)}],
                        "isError": True,
                    }
            else:
                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32601, "message": "Method not found"},
                        }
                    ),
                    flush=True,
                )
                continue
            response = {"jsonrpc": "2.0", "id": request["id"], "result": result}
        except Exception as e:
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if isinstance(request, dict) else None,
                "error": {"code": -32700, "message": str(e)},
            }
        print(json.dumps(response), flush=True)
