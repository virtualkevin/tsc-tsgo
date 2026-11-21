"""Time full checks and verify the ordered file list from the same invocation."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
reference = json.loads(gzip.decompress((here.parent / "named-key-union/public.json.gz").read_bytes()))
control, candidate = sys.argv[1:3]
env = {key: value for key, value in os.environ.items()
       if not key.startswith(("TSC_", "TS_GO_", "SCRIPTC_", "GODEBUG", "GOGC", "GOMAXPROCS", "GOMEMLIMIT"))}
env.update(reference["environment"]["compilerEnvironment"])

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

report = {"compilerHashes": [digest(control), digest(candidate)], "projects": {}}
for project in sorted(reference["projects"], key=lambda p: len(p["preflight"]["baseline"]["inputs"])):
    cwd = Path(project["cwd"])
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=cwd, text=True).strip() == project["commit"]
    inputs = project["preflight"]["baseline"]["inputs"]
    def verify_inputs():
        assert all(digest(cwd / item["file"]) == item["sha256"] for item in inputs)
    verify_inputs()
    args = project["compilerArgs"]["candidate"] + ["--listFiles"]
    expected = sorted(item["file"] for item in inputs)
    stdout_hash = None
    samples = []
    for binary in (control, candidate, candidate, control):
        start = time.monotonic_ns()
        result = subprocess.run([binary, *args], cwd=cwd, env=env, capture_output=True, check=True, timeout=480)
        elapsed = (time.monotonic_ns() - start) / 1e6
        assert not result.stderr
        assert sorted(os.path.relpath(cwd / line, cwd) for line in result.stdout.decode().splitlines()) == expected
        actual_hash = hashlib.sha256(result.stdout).hexdigest()
        if stdout_hash is None:
            stdout_hash = actual_hash
        assert actual_hash == stdout_hash
        samples.append(elapsed)
    verify_inputs()
    row = dict(commit=project["commit"], args=args, files=len(inputs), orderedOutputSha256=stdout_hash,
               controlMs=[samples[0], samples[3]], candidateMs=samples[1:3])
    report["projects"][project["name"]] = row
    print(project["name"], statistics.median(row["controlMs"]), statistics.median(row["candidateMs"]), flush=True)
    (here / "results.json").write_text(json.dumps(report, indent=2) + "\n")
