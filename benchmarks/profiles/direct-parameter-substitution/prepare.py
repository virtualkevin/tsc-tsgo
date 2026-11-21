"""Use direct substitution for an inactive, immutable simple type mapper."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True, parents=True)
path = Path("internal/checker/checker.go")
s = subprocess.check_output(["git", "show", "28cf608:packages/tsc-go/"+str(path)], cwd=root, text=True)
site = """index := c.findActiveMapper(m)
	if index == -1 {
		c.pushActiveMapper(m)"""
replacement = """index := c.findActiveMapper(m)
	if index == -1 {
		// A simple mapper substitutes one parameter without entering the checker.
		// A new activation has no cached results for recursive calls to observe.
		if t.flags&TypeFlagsTypeParameter != 0 && alias == nil {
			if simple, ok := m.data.(*SimpleTypeMapper); ok {
				c.TotalInstantiationCount++
				c.instantiationCount++
				return simple.Map(t)
			}
		}
		c.pushActiveMapper(m)"""
assert s.count(site) == 1
file = out/path.name
file.write_text(s.replace(site, replacement))
(out/"overlay.json").write_text(json.dumps({"Replace":{str(root/path):str(file)}}))

test = root / path.parent / "direct_parameter_test.go"
(out/"test-overlay.json").write_text(json.dumps({"Replace":{
    str(root/path):str(file),
    str(test):str(Path(__file__).resolve().with_name("direct_parameter_test.go.txt")),
}}))
