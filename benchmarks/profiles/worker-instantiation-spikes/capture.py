"""Attribute sampled generic instantiations to their outermost type and request site."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
replacement = {str(root / "internal/checker/instantiation_spike_probe.go"): str(here / "probe.go.txt")}


def edit(file, edits):
    path = root / file
    source = path.read_text()
    for old, new in edits:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    dest = out / path.name
    dest.write_text(source)
    replacement[str(path)] = str(dest)


edit("internal/checker/checker.go", [
    ("type Checker struct {", "type Checker struct {\n spikeCounter instantiationSpikeCounter"),
    ("c.TotalInstantiationCount++", """if s := &c.spikeCounter; s.active {
        if c.instantiationDepth == 0 { s.root, s.alias, s.node = t, alias, c.currentNode }
        s.next--
        if s.next == 0 { s.sample() }
    }
    c.TotalInstantiationCount++""")
])
edit("internal/compiler/checkerpool.go", [
    ("cb(checker, i, file)", "checker.BeginSpikeCallback(); cb(checker, i, file); checker.EndSpikeCallback(checkerIdx, file.FileName())")
])
edit("cmd/tsgo/main.go", [
    ('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
    ("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.SpikeCallbacks()); os.Exit(status)")
])
config = out / "overlay.json"
config.write_text(json.dumps({"Replace": replacement}))
binary = out / "tsgo"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay=" + str(config), "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
report = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "minimumCallbackInstantiations": 70000, "projects": {}}
for name, commit, rows in observed_projects(binary, projects={"sentry", "vscode"}):
    assert rows
    for row in rows:
        assert row["Samples"] > 0
        assert all(sum(row[key].values()) == row["Samples"] for key in ("Sites", "Origins", "Callers"))
    report["projects"][name] = {"commit": commit, "callbacks": sorted(rows, key=lambda r: -r["Instantiations"])}
    print(name, len(rows), [(r["Worker"], r["Instantiations"], max(r["Origins"],key=r["Origins"].get)) for r in report["projects"][name]["callbacks"][:4]], flush=True)
(here / "results.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
