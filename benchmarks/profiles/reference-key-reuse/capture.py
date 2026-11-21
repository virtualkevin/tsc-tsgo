"""Compare complete key sets of different instantiations on actual keyof cache misses."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
checker = root / "internal/checker/checker.go"
src = checker.read_text()
site = "var origin *Type\n\tif includeOrigin"
assert src.count(site) == 1
src = src.replace(site, "symbols, inst := c.SymbolCount, c.TotalInstantiationCount\n\t" + site)
site = "c.propertiesTypes[key] = result"
assert src.count(site) == 1
src = src.replace(site, site + "\n c.observeReferenceKeys(t,result,include,includeOrigin,symbols,inst)")
src = src.replace("type Checker struct {", "type Checker struct {\n referenceKeyProbe *referenceKeyProbe")
dest = out / "checker.go"
dest.write_text(src)
main = root / "cmd/tsgo/main.go"
src = main.read_text().replace('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"')
assert src.count("os.Exit(runMain())") == 1
m = out / "main.go"
m.write_text(src.replace("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.ReferenceKeyResults()); os.Exit(status)"))
cfg = out / "overlay.json"
cfg.write_text(json.dumps({"Replace":{str(checker):str(dest),str(main):str(m),str(checker.parent/"reference_key_reuse.go"):str(here/"probe.go.txt")}}))
binary = out / "tsgo"
subprocess.run([sys.argv[2],"build","-buildvcs=false","-overlay="+str(cfg),"-o",binary,"./cmd/tsgo"],cwd=root,check=True)
report = {"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"projects":{}}
for project, commit, workers in observed_projects(binary):
    targets = {}
    for worker in workers or []:
        for name, stats in worker["Stats"].items():
            assert stats["Misses"] == sum(stats[k] for k in ("NonFinite","NoPredecessor","SameObject","Equal","Changed"))
            targets.setdefault(name,Counter()).update(stats)
    totals = sum(targets.values(),Counter())
    ranked = sorted(targets, key=lambda k:(-targets[k]["EqualSymbols"],k))
    changes = sorted((k for k in targets if targets[k]["Changed"]),key=lambda k:(-targets[k]["Changed"],k))
    report["projects"][project] = {"commit":commit,"total":totals,"topEqualSymbols":{k:targets[k] for k in ranked[:12]},"topChanged":{k:targets[k] for k in changes[:8]}}
    print(project, totals, flush=True)
(here/"results.json").write_text(json.dumps(report,indent=2)+"\n")
