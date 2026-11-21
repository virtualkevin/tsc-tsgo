"""Build the ordered-pair candidate against the measured control's checker source."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
repo = here.parents[2]
root = repo / "packages/tsc-go"
file = "packages/tsc-go/internal/checker/lazy_properties.go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
control = out / "original.go"
control.write_bytes(subprocess.check_output(["git", "show", f"bd1baea:{file}"], cwd=repo))
candidate = out / "lazy_properties.go"
subprocess.run(["patch", "--output", candidate, control, here / "candidate.patch"], check=True)
overlay = out / "overlay.json"
overlay.write_text(json.dumps({"Replace": {str(repo / file): str(candidate)}}))
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay=" + str(overlay),
                "-o", out / "tsgo", "./cmd/tsgo"], cwd=root, check=True)
