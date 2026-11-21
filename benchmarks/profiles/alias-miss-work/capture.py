"""Charge every generic instantiation to its innermost active type alias cache miss."""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
root = here.parents[2] / "packages/tsc-go"
files = {str(root / "internal/checker/alias_miss_probe.go"): str(here / "probe.go.txt")}


def edit(file, edits):
    path = root / file
    source = path.read_text()
    for old, new in edits:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    dest = out / path.name
    dest.write_text(source)
    files[str(path)] = str(dest)


start = "mapper := newTypeMapper(typeParameters, c.fillMissingTypeArguments(typeArguments, typeParameters, ast.IsInJSFile(symbol.ValueDeclaration)))"
end = "instantiation = c.instantiateTypeWithAlias(t, mapper, alias)"
edit("internal/checker/checker.go", [
    ("type Checker struct {", "type Checker struct {\n aliasMissProbe *aliasMissProbe"),
    ("c.TotalInstantiationCount++", """p := c.aliasWork()
    if p.active != nil { p.active.Exclusive++ } else { p.Outside++ }
    c.TotalInstantiationCount++"""),
    (start, """p := c.aliasWork()
        parent := p.active
        row := p.enter(symbol)
        before := c.TotalInstantiationCount
        """ + start),
    (end, end + """
        delta := uint64(c.TotalInstantiationCount - before)
        if parent == nil { p.Outermost += delta }
        row.Inclusive += delta
        row.Largest = max(row.Largest, delta)
        p.active = parent""")
])
edit("cmd/tsgo/main.go", [
    ('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
    ("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.AliasMissProfiles()); os.Exit(status)")
])
cfg = out / "overlay.json"
cfg.write_text(json.dumps({"Replace": files}))
binary = out / "tsgo"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay=" + str(cfg), "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
report = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "projects": {}}
fixture = out / "nested.ts"
fixture.write_text("""type Inner<T> = T extends string ? { text: T } : { value: T };
type Outer<T> = T extends unknown ? Inner<T> : never;
declare let value: Outer<"a" | "b" | 1>;
const result: {text: string} | {value: number} = value;
""")
fixture_env = dict(os.environ, TSC_TS_LIB_DIR=str(root / "internal/bundled/libs"))
run = subprocess.run([binary, "--noEmit", "--skipLibCheck", "--extendedDiagnostics", fixture],
                     cwd=out, env=fixture_env, capture_output=True, text=True, check=True)
workers = json.loads(run.stderr)
official = int(re.search(r"^Instantiations:\s+(\d+)$", run.stdout, re.M)[1])
attributed = sum(w["Outside"] + sum(r["Exclusive"] for r in w["Rows"] or []) for w in workers)
assert official == attributed and attributed > 0
assert {"Inner", "Outer"} <= {r["Name"] for w in workers for r in w["Rows"] or []}
report["fixture"] = {"extendedDiagnosticsInstantiations": official, "accounted": attributed}
for project, commit, workers in observed_projects(binary):
    totals = {}
    outside = sum(w["Outside"] for w in workers)
    for w in workers:
        assert sum(r["Exclusive"] for r in w["Rows"] or []) == w["Outermost"]
        worker_work = Counter()
        for row in w["Rows"] or []:
            key = row["File"], row["Pos"], row["Name"]
            worker_work[key] += row["Exclusive"]
            stats = totals.setdefault(key, Counter())
            for metric in ("Exclusive", "Misses", "Inclusive"):
                stats[metric] += row[metric]
            stats["Largest"] = max(stats["Largest"], row["Largest"])
            assert row["Inclusive"] >= max(row["Exclusive"], row["Largest"])
        for key, work in worker_work.items():
            totals[key]["Workers"] += 1
            totals[key]["LargestWorkerExclusive"] = max(totals[key]["LargestWorkerExclusive"], work)
    ranked = sorted(totals, key=lambda k: (-totals[k]["Exclusive"], k))
    inside = sum(stats["Exclusive"] for stats in totals.values())
    assert inside > 0 and outside > 0
    report["projects"][project] = {"commit": commit, "instantiations": inside + outside, "insideMiss": inside,
        "declarations": len(ranked), "topByExclusive": [
            dict(file=f, pos=pos, name=name, **totals[f,pos,name]) for f,pos,name in ranked[:25]]}
    print(project, inside, outside, [(k[2], totals[k]["Exclusive"]) for k in ranked[:5]], flush=True)
(here / "counts.json").write_text(json.dumps(report, indent=2) + "\n")
