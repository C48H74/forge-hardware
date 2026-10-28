# Off-the-shelf parts

`forge catalog refresh` walks public repository metadata and pins raw STEP URLs to an immutable tree revision. The default is `FreeCAD/FreeCAD-library`. Use `--repo OWNER/REPO --ref BRANCH` for another public parts repository. Truncated API trees fail explicitly rather than silently yielding incomplete inventory.

The index is cached at `~/.cache/forge-hardware/catalog.json`. Search terms are ranked against paths; multiple terms improve ranking. The index contains screws, bearings, motors, connectors and electronics, but does not guarantee any particular commercial SKU. Empty results mean use a supplier search link or a user-supplied catalog. A custom catalog is a JSON list of records with `name`, `url` and optional provenance fields; the Python `catalog.search(query, cache=path)` function accepts it.

Download direct HTTPS STEP files into project assets. Keep the provenance sidecar, and optionally specify an independently verified SHA256. Exact source revision, URL, content hash and bytes are recorded. Repository license metadata is advisory: inspect the individual model and manufacturer conditions before redistributing.

The default GitHub content hosts work with HTTPS proxies. Other download hosts must resolve to public IP addresses; private/local addresses and embedded credentials are rejected, including on redirects. Network restrictions, rate limits, authentication, DNS restrictions and vendor automation policies may prevent a download. Use the vendor's normal browser/manual workflow in those cases; no login bypass is implemented.

Downloaded models are not automatically dimensionally certified. Reopen them with build123d, compare bounding dimensions to the manufacturer's drawing, inspect orientation, and then place them in your source. Never execute downloaded scripts.
