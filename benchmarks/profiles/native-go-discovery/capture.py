"""Compare fresh-process discovery, including file-list output, on both compilers."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from statistics import median
import subprocess
import tempfile
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--go-candidate", type=Path, help="compare a local Go candidate to production Go")
candidate = parser.parse_args().go_candidate
report = {"projects": {}}
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

with tempfile.TemporaryDirectory() as scratch:
    metrics = Path(scratch) / "resources"
    for group in ("small", "large"):
        old = json.loads((root / f"benchmarks/results/native-project-inlining/{group}.json").read_text())
        assert old["status"] == "passed"
        bins = dict(old["binaries"])
        if candidate:
            bins["baseline"] = bins["candidate"]
            bins["candidate"] = dict(path=str(candidate.resolve()), sha256=digest(candidate))
        for b in bins.values():
            assert digest(Path(b["path"])) == b["sha256"]
        report["binaries"] = {mode: b["sha256"] for mode, b in bins.items()}
        env = {k: v for k, v in os.environ.items() if k not in old["environment"]["unsetEnvironment"]
               and not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
        env.update(old["environment"]["compilerEnvironment"], LC_ALL="C")
        for p in old["projects"]:
            cwd = Path(p["cwd"])
            manifest = p["preflight"]["candidate"]["inputs"]
            assert manifest == p["preflight"]["baseline"]["inputs"]
            assert subprocess.check_output(["git","rev-parse","HEAD"], cwd=cwd, text=True).strip() == p["commit"]
            def verify():
                for item in manifest:
                    assert digest(cwd / item["file"]) == item["sha256"]
            verify()
            paths = sorted(f["file"] for f in manifest)
            args = p["fileDiscoveryArgs"]["baseline"]
            assert args == p["fileDiscoveryArgs"]["candidate"] and "--listFilesOnly" in args
            rows = []
            for pair in range(5):
                for mode in (("baseline","candidate") if pair % 2 == 0 else ("candidate","baseline")):
                    cmd = ["/usr/bin/time", "-f", "%U %S %M %R %F", "-o", metrics, bins[mode]["path"], *args]
                    start = time.monotonic_ns()
                    proc = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True, check=True, timeout=400)
                    ms = (time.monotonic_ns() - start) / 1e6
                    assert not proc.stderr
                    assert sorted(os.path.relpath(cwd / s, cwd) for s in proc.stdout.splitlines()) == paths
                    u, s, rss, minor, major = metrics.read_text().split()
                    rows.append(dict(pair=pair, mode=mode, ms=ms, userSeconds=float(u), systemSeconds=float(s),
                                     rssKiB=int(rss), minorFaults=int(minor), majorFaults=int(major)))
            verify()
            fields = ("ms","userSeconds","systemSeconds","rssKiB","minorFaults","majorFaults")
            summary = {m: {f: median(r[f] for r in rows if r["mode"] == m and r["pair"] > 0) for f in fields}
                       for m in bins}
            report["projects"][p["name"]] = dict(commit=p["commit"], args=args, files=len(paths), samples=rows, medians=summary)
            print(p["name"], summary, flush=True)
(here / ("thp.json" if candidate else "report.json")).write_text(json.dumps(report, indent=2) + "\n")
