"""Size the bundled-library portion of each verified public-release workload."""
import gzip
import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
ref = json.loads(gzip.decompress((here.parent / "public-npm/0.0.2.json.gz").read_bytes()))
lib = Path(ref["environment"]["compilerEnvironment"]["TSC_TS_LIB_DIR"]).resolve()
out = {}
for project in ref["projects"]:
    assert project["status"] == "passed"
    inputs = project["preflight"]["candidate"]["inputs"]
    assert inputs == project["preflight"]["baseline"]["inputs"]
    total_bytes = 0
    libraries = {}
    for entry in inputs:
        source = (Path(project["cwd"]) / entry["file"]).resolve()
        data = source.read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
        total_bytes += len(data)
        if source.parent != lib:
            continue
        assert source.name.startswith("lib.") and source.name.endswith(".d.ts")
        libraries[source.name] = len(data)
    out[project["name"]] = {
        "commit": project["commit"], "files": len(inputs), "sourceBytes": total_bytes,
        "libraryFiles": len(libraries), "libraryBytes": sum(libraries.values()),
        "libraries": dict(sorted(libraries.items())),
    }
    print(project["name"], len(libraries), sum(libraries.values()), total_bytes)
(here / "shares.json").write_text(json.dumps(out, indent=2) + "\n")
