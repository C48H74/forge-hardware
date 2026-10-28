"""Serialized, token-protected local build requests; subprocess per build."""

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json
import secrets
import subprocess
import sys


def serve(workspace, port=8741):
    workspace = Path(workspace).resolve()
    token = secrets.token_urlsafe(32)
    print(f"Build daemon http://127.0.0.1:{port}\nToken: {token}", flush=True)

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if (
                self.path != "/build"
                or self.headers.get("Authorization") != f"Bearer {token}"
            ):
                self.send_error(403)
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 65536:
                    raise ValueError("Invalid body size")
                body = json.loads(self.rfile.read(size))
                source, output = (
                    Path(body["source"]).resolve(),
                    Path(body["output"]).resolve(),
                )
                if not all(p.is_relative_to(workspace) for p in [source, output]):
                    raise ValueError("Paths must stay within workspace")
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
                        json.dumps(body.get("parameters", {})),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                response = {
                    "ok": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
                data = json.dumps(response).encode()
                self.send_response(200 if response["ok"] else 422)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_error(400, str(e))

    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
