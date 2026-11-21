"""Compare cached finite mapped-base constraints with actual inherited property names."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

root = here.parents[2]/"packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
pending = root/"internal/checker/pending_members.go"
site = "base.properties = c.getPropertiesOfType(instantiatedBaseType)"
s = pending.read_text()
assert s.count(site) == 1
dest = out/"pending.go"
dest.write_text(s.replace(site,"base.properties = c.observeMappedBaseProperties(instantiatedBaseType)"))
main = root/"cmd/tsgo/main.go"
s = main.read_text().replace('"context"','"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"')
assert s.count("os.Exit(runMain())") == 1
m = out/"main.go"
m.write_text(s.replace("os.Exit(runMain())","status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.MappedBaseKeyCounts()); os.Exit(status)"))
cfg = out/"overlay.json"
cfg.write_text(json.dumps({"Replace":{str(main):str(m),str(pending):str(dest),str(pending.parent/"mapped_base_probe.go"):str(here/"observer.go.txt")}}))
binary = out/"tsgo"
subprocess.run([sys.argv[2],"build","-buildvcs=false","-overlay="+str(cfg),"-o",binary,"./cmd/tsgo"],cwd=root,check=True)
columns = "unresolvedMapped ordinaryConstraint finite cached mismatchedNames properties symbols instantiations cachedSymbols cachedInstantiations unexpectedStructure wide".split()
report = {"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"projects":{}}
for project,commit,counts in observed_projects(binary):
    r = dict(zip(columns,counts,strict=True))
    assert r["cached"] <= r["finite"] <= r["ordinaryConstraint"] <= r["unresolvedMapped"]
    report["projects"][project] = {"commit":commit,"counts":r}
    print(project,r,flush=True)
(here/"results.json").write_text(json.dumps(report,indent=2)+"\n")
