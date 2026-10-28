"""Repeat real exports and report measured timings, without quality claims."""

from pathlib import Path
import argparse
import json
import platform
import statistics
import tempfile
import time
import importlib.metadata
from forge_hardware.cad.artifacts import build


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--output", default="benchmarks/results.json")
    args = p.parse_args()
    if args.runs < 1:
        p.error("--runs must be positive")
    root = Path(__file__).resolve().parents[1]
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for example in ["fixture", "bracket", "robot_arm"]:
            samples = []
            for i in range(args.runs):
                start = time.perf_counter()
                manifest = build(
                    root / "examples" / f"{example}.py", Path(tmp) / example
                )
                samples.append(time.perf_counter() - start)
            rows.append(
                {
                    "example": example,
                    "samples_seconds": samples,
                    "median_seconds": statistics.median(samples),
                    "artifact_count": len(manifest["files"]),
                }
            )
    report = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "build123d": importlib.metadata.version("build123d"),
        "scope": "Warm-process geometry and export latency. No LLM latency, cold imports, fabrication or simulation validation.",
        "results": rows,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
