"""STEP operations and the script-to-build-daemon boundary."""

from pathlib import Path
import json
import urllib.request
from build123d import import_step
from .build123d import Part


def load_part(path, part_id, **kwargs):
    return Part(part_id, import_step(str(Path(path).resolve())), **kwargs)


def request_build(
    source, output, daemon="http://127.0.0.1:8741", token=None, parameters=None
):
    data = json.dumps(
        {
            "source": str(Path(source).resolve()),
            "output": str(Path(output).resolve()),
            "parameters": parameters or {},
        }
    ).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(daemon + "/build", data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=300) as response:
        return json.load(response)
