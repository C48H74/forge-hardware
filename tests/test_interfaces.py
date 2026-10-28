import json
import subprocess
import sys
from pathlib import Path
import pytest
from forge_hardware import catalog

ROOT = Path(__file__).resolve().parents[1]


def test_catalog_search_and_download_validation(tmp_path, monkeypatch):
    cache = tmp_path / "catalog.json"
    cache.write_text(
        json.dumps([{"name": "bearings/608.step"}, {"name": "screws/M3.step"}])
    )
    assert catalog.search("608 bearing", cache)[0]["name"] == "bearings/608.step"
    monkeypatch.setattr(catalog, "get", lambda url: b"<!doctype html>sign in")
    with pytest.raises(ValueError):
        catalog.download("https://example.com/x.step", tmp_path / "x.step")
    monkeypatch.setattr(catalog, "get", lambda url: b"ISO-10303-21;\nEND-ISO-10303-21;")
    with pytest.raises(ValueError):
        catalog.download("https://example.com/x.step", tmp_path / "x.step", "0" * 64)
    result = catalog.download("https://example.com/x.step", tmp_path / "x.step")
    assert len(result["sha256"]) == 64 and (tmp_path / "x.step.json").exists()
    with pytest.raises(FileExistsError):
        catalog.download("https://example.com/x.step", tmp_path / "x.step")


def test_private_download_rejected():
    for url in [
        "http://example.com/x.step",
        "https://127.0.0.1/x.step",
        "https://user:pass@example.com/x.step",
    ]:
        with pytest.raises(ValueError):
            catalog.public_url(url)


def test_mcp_protocol_and_path_boundary(tmp_path):
    messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"},
        },
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "inspect_design", "arguments": {"output": "../escape"}},
        },
    ]
    p = subprocess.run(
        [sys.executable, "-m", "forge_hardware", "mcp", "--workspace", str(tmp_path)],
        input="\n".join(map(json.dumps, messages)) + "\n",
        text=True,
        capture_output=True,
        check=True,
    )
    replies = list(map(json.loads, p.stdout.splitlines()))
    assert replies[0]["result"]["serverInfo"]["name"] == "forge-hardware"
    assert len(replies[1]["result"]["tools"]) == 5
    assert replies[2]["result"]["isError"] is True
