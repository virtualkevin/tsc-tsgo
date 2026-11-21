"""Measure rejected finite-string pairs while still executing ordinary relations."""
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
relater = root / "internal/checker/relater.go"
src = relater.read_text()
marker = "func (c *Checker) isTypeRelatedTo(source *Type, target *Type, relation *Relation) bool {"
assert src.count(marker) == 1
src = src.replace(marker, marker + """
	if source.flags&TypeFlagsStringLiteral != 0 && target.flags&TypeFlagsTemplateLiteral != 0 &&
		unmatchedTemplateIndexKey(source, target.AsTemplateLiteralType()) {
		before, flags := c.TotalInstantiationCount, c.reliabilityFlags
		sizes := len(relation.results)
		result := c.originalTypeRelatedTo(source, target, relation)
		entryObservations[0].Add(1)
		if result { entryObservations[1].Add(1) }
		if c.reliabilityFlags != flags { entryObservations[2].Add(1) }
		if before != c.TotalInstantiationCount { entryObservations[3].Add(1) }
		if len(relation.results) > sizes { entryObservations[4].Add(1) }
		return result
	}
	return c.originalTypeRelatedTo(source, target, relation)
}

func (c *Checker) originalTypeRelatedTo(source *Type, target *Type, relation *Relation) bool {""")
src = src.replace("import (", 'import (\n"sync/atomic"', 1)
src += """
var entryObservations [5]atomic.Uint64
func FiniteEntryObservations() [5]uint64 {
    var out [5]uint64
    for i := range out { out[i] = entryObservations[i].Load() }
    return out
}
"""
dest = out / "observed_relater.go"
dest.write_text(src)
main = root / "cmd/tsgo/main.go"
src = main.read_text().replace('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"')
assert src.count("os.Exit(runMain())") == 1
src = src.replace("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.FiniteEntryObservations()); os.Exit(status)")
destmain = out / "observed_main.go"
destmain.write_text(src)
cfg = out / "observations.json"
cfg.write_text(json.dumps({"Replace": {str(relater):str(dest), str(main):str(destmain)}}))
binary = out / "observer"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay=" + str(cfg), "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
report = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
          "columns": ["eligible", "returnedTrue", "changedReliability", "performedInstantiations", "increasedRelationSize"], "projects": {}}
for project, commit, row in observed_projects(binary):
    assert len(row) == 5 and row[0] >= max(row[1:])
    report["projects"][project] = {"commit": commit, "counts": row}
    print(project, row, flush=True)
(here / "observations.json").write_text(json.dumps(report, indent=2) + "\n")
