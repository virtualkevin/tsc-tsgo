"""Build a Go overlay for conditional inference with an empty branch."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
path = Path("packages/tsc-go/internal/checker/inference.go")
s = subprocess.check_output(["git", "show", f"8d9a8c3:{path}"], cwd=root, text=True)
old = """targetTypes := []*Type{c.getTrueTypeFromConditionalType(target), c.getFalseTypeFromConditionalType(target)}
		c.inferToMultipleTypesWithPriority(n, source, targetTypes, target.flags, core.IfElse(n.contravariant, InferencePriorityContravariantConditional, 0))"""
new = """trueType := c.getTrueTypeFromConditionalType(target)
		falseType := c.getFalseTypeFromConditionalType(target)
		priority := core.IfElse(n.contravariant, InferencePriorityContravariantConditional, 0)
		if trueType.flags&TypeFlagsNever != 0 || falseType.flags&TypeFlagsNever != 0 {
			remaining := trueType
			if remaining.flags&TypeFlagsNever != 0 {
				remaining = falseType
			}
			if getInferenceInfoForType(n, remaining) != nil {
				priority |= InferencePriorityNakedTypeVariable
			}
			c.inferWithPriority(n, source, remaining, priority)
			return
		}
		c.inferToMultipleTypesWithPriority(n, source, []*Type{trueType, falseType}, target.flags, priority)"""
assert s.count(old) == 1
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
replacement = out/path.name
replacement.write_text(s.replace(old,new))
(out/"overlay.json").write_text(json.dumps({"Replace":{str(root/path):str(replacement)}}))
test_path = root / path.parent / "never_branch_test.go"
(out/"test-overlay.json").write_text(json.dumps({"Replace":{
    str(root/path):str(replacement),
    str(test_path):str(Path(__file__).resolve().with_name("branch_test.go.txt")),
}}))
