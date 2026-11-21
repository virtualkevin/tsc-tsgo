"""Capture alloc_space before and after two final GCs in the same Sentry process."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
go = sys.argv[2]
ref = json.loads(gzip.decompress((here.parent / "ordered-intersection-pair/screen.json.gz").read_bytes()))
p = next(p for p in ref["projects"] if p["name"] == "sentry")
cwd = Path(p["cwd"])
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=cwd, text=True).strip() == p["commit"]
for f in p["preflight"]["candidate"]["inputs"]:
    assert hashlib.sha256((cwd / f["file"]).read_bytes()).hexdigest() == f["sha256"]
env = {k: v for k,v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env.update(ref["environment"]["compilerEnvironment"])
profiler = root / "internal/pprof/pprof.go"
src = profiler.read_text()
site = 'memFile, err := os.Create(p.memFilePath)'
assert src.count(site) == 1
src = src.replace(site, """var stats runtime.MemStats
        runtime.ReadMemStats(&stats)
        fmt.Fprintf(p.logWriter, "TotalAlloc before profiling: %d\\n", stats.TotalAlloc)
        memFile, err := os.Create(p.memFilePath)""")
site = 'memFile.Close()'
assert src.count(site) == 1
src = src.replace(site, """memFile.Close()
        runtime.GC()
        runtime.GC()
        if _, err := SaveAllocProfile(filepath.Dir(p.memFilePath)); err != nil { panic(err) }
        runtime.ReadMemStats(&stats)
        fmt.Fprintf(p.logWriter, "TotalAlloc after profiling: %d\\n", stats.TotalAlloc)""")
dest = out / "terminal_pprof.go"
dest.write_text(src)
report = {"projectCommit": p["commit"], "args": p["compilerArgs"]["candidate"], "binaries": {}}
for role in ("control", "candidate"):
    files = json.loads((out / "overlay.json").read_text())["Replace"] if role == "candidate" else {}
    files[str(profiler)] = str(dest)
    overlay = out / (role + "-terminal.json")
    overlay.write_text(json.dumps({"Replace": files}))
    binary = out / (role + "-terminal")
    subprocess.run([go, "build", "-buildvcs=false", "-overlay=" + str(overlay), "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
    entry = {"sha256": hashlib.sha256(binary.read_bytes()).hexdigest()}
    with tempfile.TemporaryDirectory() as temp:
        run = subprocess.run([binary, *report["args"], "--pprofDir", temp], cwd=cwd, env=env, check=True, timeout=480, capture_output=True, text=True)
        assert not run.stderr and len(run.stdout.splitlines()) == 4
        for when in ("before", "after"):
            value, = re.findall(rf"^TotalAlloc {when} profiling: (\d+)$", run.stdout, re.M)
            entry[when + "TotalAlloc"] = int(value)
        for stage, suffix in (("before","memprofile"), ("after","allocprofile")):
            file, = Path(temp).glob(f"*-{suffix}.pb.gz")
            dest = here / f"sentry-{role}-{stage}-gc.pb.gz"
            dest.write_bytes(file.read_bytes())
            top = subprocess.check_output([go,"tool","pprof","-top","-sample_index=alloc_space","-unit=bytes","-nodefraction=0","-nodecount=0",dest],text=True)
            total = int(re.search(r"100% of (\d+)B total", top)[1])
            methods = {}
            for fn in ("(*Checker).addInheritedMembers", "(*pendingInstantiatedMembers).ownTable"):
                row, = [r for r in top.splitlines() if r.endswith("internal/checker." + fn)]
                methods[fn] = int(row.split()[0].removesuffix("B"))
            entry[stage] = {"profileSha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
                            "sampledAllocatedBytes": total, "flatAllocatedBytes": methods, "combinedFlatBytes": sum(methods.values())}
    report["binaries"][role] = entry
    print(role, entry, flush=True)
(here / "terminal-profiles.json").write_text(json.dumps(report, indent=2) + "\n")
