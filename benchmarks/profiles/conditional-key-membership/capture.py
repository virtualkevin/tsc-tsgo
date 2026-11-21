"""Measure the ordinary extends operand for fixed-string versus keyof conditionals."""
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
references = sys.argv[3:] == ["--references"]
shapes = references or sys.argv[3:] == ["--shapes"]
predict = shapes or sys.argv[3:] == ["--predict"]
assert predict or len(sys.argv) == 3
checker = root / "internal/checker/checker.go"
source = checker.read_text()
site = "extendsType := c.instantiateType(root.extendsType, mapper)"
assert source.count(site) == 1
source = source.replace(site, "extendsType := c.observeKeyOperand(root, mapper, checkType)")
assert source.count("type Checker struct {") == 1
source = source.replace("type Checker struct {", "type Checker struct {\n keyOperandProbe *keyOperandProbe\n keyRequest *keyOperandRequest")
lookup = "return c.getIndexType(c.instantiateType(t.Target(), m))"
assert source.count(lookup) == 1
source = source.replace(lookup, """object := c.instantiateType(t.Target(), m)
        if req := c.keyRequest; req != nil && req.target == t && req.mapper == m && !req.seen {
            req.record(c, object)
        }
        return c.getIndexType(object)""")
dest = out / "checker.go"
dest.write_text(source)
main = root / "cmd/tsgo/main.go"
main_src = main.read_text().replace('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"')
assert main_src.count("os.Exit(runMain())") == 1
manifest = out / "main.go"
manifest.write_text(main_src.replace("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.KeyOperandResults()); os.Exit(status)"))
cfg = out / "overlay.json"
cfg.write_text(json.dumps({"Replace": {str(checker): str(dest), str(main): str(manifest),
                                     str(checker.parent / "key_operand_probe.go"): str(here / "probe.go.txt")}}))
if predict:
    mod = json.loads(cfg.read_text())
    mod["Replace"][str(checker.parent / "key_prediction.go")] = str(here / "prediction.go.txt")
    probe = (here / "probe.go.txt").read_text()
    probe = probe.replace("type keyOperandStats struct {", "type keyOperandStats struct {\n keyPredictionStats")
    probe = probe.replace("type keyOperandRequest struct {", "type keyOperandRequest struct {\n keyPrediction")
    probe = probe.replace("q.seen = true", "q.seen = true\n q.predict(c, object)")
    probe = probe.replace("c.keyRequest = &keyOperandRequest{", "request := &keyOperandRequest{")
    probe = probe.replace("result := c.instantiateType", "request.text = getStringLiteralValue(checkType)\n c.keyRequest = request\n result := c.instantiateType")
    probe = probe.replace("c.keyRequest = previous", "c.keyRequest = previous\n request.compare(c, result)")
    if shapes:
        probe = probe.replace("type keyOperandRequest struct {", "type keyOperandRequest struct {\n shape string")
        probe = probe.replace("q.predict(c, object)", "q.predict(c, object)\n q.shape = indexObjectShape(object)")
        probe = probe.replace("request.compare(c, result)", "request.compare(c, result)\n c.observeKeyShape(request, cohort, result, types, syms, inst)")
        mod["Replace"][str(checker.parent / "key_shape.go")] = str(here / "shape.go.txt")
    if references:
        probe = probe.replace("type keyOperandRequest struct {", "type keyOperandRequest struct {\n reference *Type")
        probe = probe.replace("q.shape = indexObjectShape(object)", "q.shape = indexObjectShape(object)\n if q.shape == \"unresolved reference\" { q.reference = object }")
        site = "return c.resolveStructuredTypeMembers(t).Properties()"
        assert source.count(site) == 1
        dest.write_text(source.replace(site, """if q := c.keyRequest; q != nil && q.reference == t {
            return c.observeReferenceProperties(t, q)
        }
        """ + site))
        mod["Replace"][str(checker.parent / "reference_stages.go")] = str(here / "reference_stages.go.txt")
    dest_probe = out / "key_operand_probe.go"
    dest_probe.write_text(probe)
    mod["Replace"][str(checker.parent / "key_operand_probe.go")] = str(dest_probe)
    cfg.write_text(json.dumps(mod))
binary = out / "tsgo"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay=" + str(cfg), "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
report = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "projects": {}}
for project, commit, workers in observed_projects(binary, projects={"sentry"} if shapes else None):
    result = {}
    for worker in workers or []:
        for name, stats in worker.items():
            total = result.setdefault(name, dict.fromkeys(stats, 0))
            for key, count in stats.items():
                total[key] = max(total[key], count) if key == "MaxWidth" else total[key] + count
    if shapes:
        for name in ("className", "other"):
            branches = [stats for label, stats in result.items() if label.startswith(name + "/")]
            for metric in ("Calls", "Union", "WideUnion", "NewWideUnion", "TypesCreated", "SymbolsCreated", "Instantiations"):
                assert sum(b[metric] for b in branches) == result[name][metric]
    for stats in result.values():
        assert stats["NewWideUnion"] <= stats["WideUnion"] <= stats["Union"] <= stats["Calls"]
        assert stats["CachedOrdinaryKeys"] <= stats["ResolvedOrdinaryObject"] <= stats["ObjectQueries"] <= stats["Calls"]
    if references:
        metrics = ("Calls", "SymbolsCreated", "TypesCreated", "Instantiations")
        for label, stats in result.items():
            if label.startswith("reference:"):
                result[label] = {metric: stats[metric] for metric in metrics}
    report["projects"][project] = {"commit": commit, "byLiteral": result}
    print(project, result, flush=True)
(here / ("references.json" if references else "shapes.json" if shapes else "predictions.json" if predict else "counts.json")).write_text(json.dumps(report, indent=2) + "\n")
