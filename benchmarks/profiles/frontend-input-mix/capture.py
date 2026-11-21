"""Partition the exact frozen compiler inputs by declaration kind and path."""
import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[2]
libs = (root / "upstream/typescript-go/internal/bundled/libs").resolve()
report = {}
for group in ("small","large"):
    ref = json.loads((root / f"benchmarks/results/native-project-inlining/{group}.json").read_text())
    for project in ref["projects"]:
        cwd = Path(project["cwd"])
        groups = {}
        inputs = project["preflight"]["candidate"]["inputs"]
        for row in inputs:
            path = (cwd / row["file"]).resolve()
            data = path.read_bytes()
            assert hashlib.sha256(data).hexdigest() == row["sha256"]
            if path.is_relative_to(libs):
                key = "compiler library"
            else:
                category = "node_modules" if "node_modules" in path.parts else "project or workspace"
                kind = "declaration" if path.name.endswith((".d.ts",".d.cts",".d.mts")) else "other input"
                key = f"{category} / {kind}"
            totals = groups.setdefault(key, {"files":0,"bytes":0})
            totals["files"] += 1
            totals["bytes"] += len(data)
        assert len(inputs)==sum(x["files"] for x in groups.values())
        report[project["name"]] = dict(commit=project["commit"], files=len(inputs),
                                        bytes=sum(x["bytes"] for x in groups.values()), groups=groups)
(here / "results.json").write_text(json.dumps(report,indent=2)+"\n")
