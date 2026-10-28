"""Read-only loopback viewer; no model execution or hosted dependencies."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import webbrowser


def serve(output, port=8740, open_browser=True):
    output = Path(output).resolve()
    if not (output / "manifest.json").exists():
        raise ValueError("Build a design first")
    assets = Path(__file__).parent
    for name in ["index.html", "client.js", "runtime.js", "i18n.js"]:
        shutil.copyfile(assets / name, output / name)

    class Handler(SimpleHTTPRequestHandler):
        def translate_path(self, path):
            candidate = Path(super().translate_path(path)).resolve()
            if not candidate.is_relative_to(output):
                return str(output / "__forbidden__")
            return str(candidate)

        def end_headers(self):
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'self'",
            )
            super().end_headers()

    server = ThreadingHTTPServer(
        ("127.0.0.1", port), partial(Handler, directory=str(output))
    )
    url = f"http://127.0.0.1:{server.server_port}"
    print(url, flush=True)
    if open_browser:
        webbrowser.open(url)
    server.serve_forever()
