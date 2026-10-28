"""Search a pinned public STEP index; retain provenance and content hashes."""

from pathlib import Path
import hashlib
import json
import urllib.request
from urllib.parse import quote, urlparse
import ipaddress
import socket

CACHE = Path.home() / ".cache" / "forge-hardware" / "catalog.json"


def public_url(url):
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Use a public HTTPS URL without embedded credentials")
    # Fixed public content services also work behind DNS-isolating HTTPS proxies.
    if parsed.hostname in {
        "api.github.com",
        "raw.githubusercontent.com",
    } and parsed.port in {None, 443}:
        return url
    for result in socket.getaddrinfo(parsed.hostname, parsed.port or 443):
        if not ipaddress.ip_address(result[4][0]).is_global:
            raise ValueError("Private/local network downloads are disallowed")
    return url


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get(url, limit=100_000_000):
    public_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": "forge-hardware/0.1"})
    with urllib.request.build_opener(SafeRedirect()).open(req, timeout=60) as response:
        data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError("Download exceeds size limit")
        return data


def refresh(cache=CACHE, repo="FreeCAD/FreeCAD-library", ref="master"):
    if len(repo.split("/")) != 2 or any(
        not x.replace("-", "").replace("_", "").replace(".", "").isalnum()
        for x in repo.split("/")
    ):
        raise ValueError("Expected owner/repository")
    tree = json.loads(
        get(
            f"https://api.github.com/repos/{repo}/git/trees/{quote(ref, safe='')}?recursive=1",
            20_000_000,
        )
    )
    if tree.get("truncated"):
        raise ValueError("Truncated index: use a smaller repository or curated catalog")
    revision = tree["sha"]
    records = []
    for entry in tree["tree"]:
        path = entry["path"]
        if entry["type"] == "blob" and path.lower().endswith((".step", ".stp")):
            records.append(
                {
                    "id": entry["sha"],
                    "name": path,
                    "repository": repo,
                    "revision": revision,
                    "url": f"https://raw.githubusercontent.com/{repo}/{revision}/{quote(path)}",
                    "license": "Check repository and individual part license before redistribution",
                }
            )
    cache = Path(cache)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(records, indent=2))
    return {"parts": len(records), "cache": str(cache), "revision": revision}


def search(query, cache=CACHE, limit=20):
    terms = query.lower().split()
    if not Path(cache).exists():
        refresh(cache)
    records = json.loads(Path(cache).read_text())
    ranked = [
        (sum(term in row["name"].lower() for term in terms), row) for row in records
    ]
    return [
        row
        for score, row in sorted(ranked, key=lambda p: (-p[0], p[1]["name"]))
        if score > 0
    ][:limit]


def download(url, destination, sha256=None, metadata=None):
    destination = Path(destination)
    if destination.suffix.lower() not in {".step", ".stp"}:
        raise ValueError("Destination must end in .step or .stp")
    if destination.exists():
        raise FileExistsError(destination)
    data = get(url)
    if b"ISO-10303-21" not in data[:4096]:
        raise ValueError(
            "Response is not an ISO STEP file (login/HTML/LFS responses rejected)"
        )
    actual = hashlib.sha256(data).hexdigest()
    if sha256 and actual.lower() != sha256.lower():
        raise ValueError("SHA256 mismatch")
    provenance = {**(metadata or {}), "url": url, "sha256": actual, "bytes": len(data)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    destination.with_suffix(destination.suffix + ".json").write_text(
        json.dumps(provenance, indent=2)
    )
    return provenance


def suppliers(query):
    return [
        {
            "name": name,
            "url": f"https://www.google.com/search?q={quote('site:' + domain + ' ' + query + ' STEP CAD')}",
        }
        for name, domain in [
            ("TraceParts", "traceparts.com"),
            ("3D ContentCentral", "3dcontentcentral.com"),
            ("McMaster-Carr", "mcmaster.com"),
            ("SnapEDA", "snapeda.com"),
            ("GrabCAD", "grabcad.com"),
        ]
    ]
