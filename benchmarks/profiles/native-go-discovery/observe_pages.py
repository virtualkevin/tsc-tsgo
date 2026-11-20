"""Sample resident anonymous huge pages in separate, untimed VS Code discovery runs."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
old = json.loads((root / "benchmarks/results/native-project-inlining/large.json").read_text())
project = next(p for p in old["projects"] if p["name"] == "vscode")
cwd = Path(project["cwd"])
expected = sorted(i["file"] for i in project["preflight"]["baseline"]["inputs"])
env = {k:v for k,v in os.environ.items() if k not in old["environment"]["unsetEnvironment"]
       and not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env.update(old["environment"]["compilerEnvironment"])
report = {"thpPolicy": Path("/sys/kernel/mm/transparent_hugepage/enabled").read_text().strip(), "runs": {}}
disabled = sys.argv[2:] == ["--disable-thp"]
assert disabled or len(sys.argv) == 2
runs = [("native", old["binaries"]["baseline"]["path"]), ("go", old["binaries"]["candidate"]["path"]),
        ("goHeapAdvice", sys.argv[1])]
if disabled:
    env["GODEBUG"] = "disablethp=1"
    runs = [("goHeapAdviceDisabled", sys.argv[1])]
for mode, binary in runs:
    rows = []
    with tempfile.TemporaryFile(mode="w+") as stdout:
        proc = subprocess.Popen([binary, *project["fileDiscoveryArgs"]["baseline"]], cwd=cwd, env=env, stdout=stdout, stderr=subprocess.PIPE)
        rollup = Path(f"/proc/{proc.pid}/smaps_rollup")
        try:
            while proc.poll() is None:
                try:
                    lines = rollup.read_text().splitlines()
                except (FileNotFoundError, ProcessLookupError):
                    break
                fields = {r.split()[0][:-1]: int(r.split()[1]) for r in lines if r.startswith(("Rss:", "AnonHugePages:"))}
                if len(fields) == 2:
                    rows.append(fields)
                time.sleep(0.1)
        finally:
            _, err = proc.communicate(timeout=400)
        assert not err and proc.returncode == 0
        stdout.seek(0)
        assert sorted(os.path.relpath(cwd / s, cwd) for s in stdout.read().splitlines()) == expected
    assert rows
    report["runs"][mode] = {"samples":rows, "peakObservedHugeKiB":max(r["AnonHugePages"] for r in rows)}
    print(mode, report["runs"][mode]["peakObservedHugeKiB"], flush=True)
(here / ("pages-disabled.json" if disabled else "pages.json")).write_text(json.dumps(report,indent=2)+"\n")
