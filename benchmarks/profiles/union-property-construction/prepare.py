"""Generate the plain-object apparent-type experiment against the shipping source."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]/"packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
file = "internal/checker/checker.go"
source = subprocess.check_output(["git","show","bd1baea:packages/tsc-go/"+file],cwd=root,text=True)
start = "func (c *Checker) getReducedApparentType(t *Type) *Type {"
assert source.count(start)==1
source = source.replace(start,start+"""
    // An ordinary object is already reduced and apparent. Mapped objects can
    // instead expose their constraint, and must run apparent-type resolution.
    if t.flags == TypeFlagsObject && t.objectFlags&ObjectFlagsMapped == 0 {
        return t
    }
    return c.reduceApparentType(t)
}

func (c *Checker) reduceApparentType(t *Type) *Type {""")
dest = out/"checker.go"
dest.write_text(source)
(out/"overlay.json").write_text(json.dumps({"Replace":{str(root/file):str(dest)}}))
