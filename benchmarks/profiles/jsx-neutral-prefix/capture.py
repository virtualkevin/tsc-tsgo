"""Count full ordinary calls bypassed and read-only property probes used to prove a prefix."""
from pathlib import Path
import hashlib
import subprocess
import json
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
bounded = "--bounded" in sys.argv[3:]
subprocess.run([sys.executable, here/"prepare.py", out, *(["--bounded"] if bounded else [])], check=True)
overlay = json.loads((out/"overlay.json").read_text())["Replace"]
objects = "--objects" in sys.argv[3:]
if objects:
    jsx = root/"internal/checker/jsx.go"
    del overlay[str(jsx)]
    checker = root/"internal/checker/checker.go"
    source = checker.read_text()
    site = "discriminated = c.discriminateTypeByDiscriminableItems(contextualType, discriminator)"
    assert source.count(site) == 1
    patch = """if len(discriminantProperties) == 0 && len(discriminantMembers) >= 8 && len(contextualType.Types()) <= 16 {
        discriminated = c.discriminateAbsentMembers(contextualType, discriminator)
    } else {
        """ + site + "\n}"
    (out/"checker.go").write_text(source.replace(site, patch))
    overlay[str(checker)] = str(out/"checker.go")
path = out / "prefix.go"
s = path.read_text().replace('import "slices"', 'import "slices"\nimport "sync/atomic"')
s = s.replace("end := len(members)", "var probes uint64\n defer func(){prefixStats[0].Add(probes)}()\n end := len(members)")
s = s.replace("prop := table[member.Name]", "probes++\n prop := table[member.Name]")
site = "n += c.neutralAbsentPrefix(types, include, discriminator.members[n:])"
if bounded:
    site = site.replace("members[n:]", "members[n:end]")
assert s.count(site) == 1
s = s.replace(site, """start := n
        """ + site + """
        var survivors uint64
        for _,v := range include { if v != TernaryFalse { survivors++ } }
        prefixStats[1].Add(1)
        prefixStats[2].Add(uint64(n-start))
        prefixStats[3].Add(uint64(n-start)*survivors)
        """)
site = "matched := false"
assert s.count(site) == 1
s = s.replace(site, "prefixStats[4].Add(survivors)\n" + site)
path.write_text(s + """
var prefixStats [5]atomic.Uint64
func NeutralPrefixCounts() (counts [5]uint64) {
    for i := range counts { counts[i]=prefixStats[i].Load() }
    return
}
""")
main = root/"cmd/tsgo/main.go"
s = main.read_text().replace('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"')
site = "os.Exit(runMain())"
assert s.count(site) == 1
(out/"main.go").write_text(s.replace(site, "status:=runMain(); json.NewEncoder(os.Stderr).Encode(checker.NeutralPrefixCounts()); os.Exit(status)"))
overlay[str(main)] = str(out/"main.go")
cfg = out / "observer.json"
cfg.write_text(json.dumps({"Replace": overlay}))
binary = out/"observer"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay="+str(cfg), "-o", binary, "./cmd/tsgo"], cwd=root,check=True)
report = {"sha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "projects": {}}
for name,commit,counts in observed_projects(binary, projects={"sentry"} if bounded else None):
    probes,passes,names,skipped,ordinary = counts
    assert probes >= skipped
    report["projects"][name] = dict(commit=commit, propertyTableReads=probes, prefixAttempts=passes,
                                    skippedNames=names, bypassedOrdinaryLookups=skipped, ordinaryLookups=ordinary)
    print(name,counts,flush=True)
(here/("bounded-counts.json" if bounded else "object-counts.json" if objects else "counts.json")).write_text(json.dumps(report,indent=2)+"\n")
