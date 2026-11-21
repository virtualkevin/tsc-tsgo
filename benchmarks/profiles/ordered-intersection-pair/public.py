"""Measure the layout candidate with the original release's launcher, binary and libraries."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
repo = here.parents[2]
reference = json.loads(gzip.decompress((here.parent / "public-npm/0.0.2.json.gz").read_bytes()))
identity = json.loads((here.parent / "jsx-absent-discriminants/groups-public-package.json").read_text())["packages"]
launcher = Path(reference["binaries"]["baseline"]["path"])
candidate = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()


def verify_release():
    for name, entry in identity.items():
        path = Path(entry["executable"])
        package = json.loads((path.parents[1] / "package.json").read_text())
        assert package["name"] == name and package["version"] == entry["version"] == "0.0.2"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
    assert launcher.resolve() == Path(identity["tsc-ts"]["executable"])


verify_release()
env = {k: v for k, v in os.environ.items() if not k.startswith(("SCRIPTC_", "TSC_", "TS_GO_"))}
env.update(reference["environment"]["compilerEnvironment"])
assert env["TSC_TS_LIB_DIR"] == str(Path(identity["@tsc-ts/linux-x64-gnu"]["executable"]).parent)
subprocess.run(["node", "benchmarks/run.mjs", "--baseline", launcher, "--candidate", candidate,
                "--projects", "vscode,sentry,typeorm,trpc", "--runs", "2", "--warmups", "0",
                "--measure-rss", "--output", output], cwd=repo, env=env, check=True)
verify_release()
subprocess.run([sys.executable, here / "record.py", output, candidate, "layout-public"], check=True)
