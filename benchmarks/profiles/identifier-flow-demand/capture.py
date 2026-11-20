"""Run the observer binary against the previously measured cold-check inputs."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

directory = Path(__file__).resolve().parent
root = directory.parents[2]
binary = Path(sys.argv[1]).resolve()
report = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "projects": []}
for group in ("small", "large"):
    source = directory.parent / "arena-fast-allocation" / (group + ".json.gz")
    run = json.loads(gzip.decompress(source.read_bytes()))
    for project in run["projects"]:
        cwd = Path(project["cwd"])
        inputs = project["preflight"]["baseline"]["inputs"]
        assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=cwd, text=True).strip() == project["commit"]
        for item in inputs:
            assert hashlib.sha256((cwd / item["file"]).read_bytes()).hexdigest() == item["sha256"]
        env = {k: v for k, v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_"))}
        env.update(run["environment"]["compilerEnvironments"]["baseline"], TSC_FLOW_REPORT="1")
        result = subprocess.run([binary, *project["compilerArgs"]["baseline"]], cwd=cwd,
                                env=env, capture_output=True, check=True)
        assert not result.stdout, result.stdout
        bound, populated, accessed, accessed_populated = map(int, result.stderr.split())
        assert 0 < accessed_populated <= min(populated, accessed) <= max(populated, accessed) <= bound
        row = dict(project=project["name"], commit=project["commit"], inputs=len(inputs),
                   bound=bound, boundNonNil=populated, accessorAfterBinding=accessed,
                   nonNilAtFirstAccess=accessed_populated)
        print(row, flush=True)
        report["projects"].append(row)
(directory / "counts.json").write_text(json.dumps(report, indent=2) + "\n")
