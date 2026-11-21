"""Reconstruct the initial reverse-copy prototype measured in reverse-scaling.json."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
path = Path("packages/tsc-go/internal/checker/checker.go")
control = subprocess.check_output(["git", "show", f"7d69a8d:{path}"], cwd=root, text=True)
start = control.index("func (c *Checker) removeStringLiteralsMatchedByTemplateLiterals")
end = control.index("\nfunc ",start+1)
body = control[start:end]
body = body.replace("i := len(types)", """// Keep the surviving suffix in place until the first removal, then pack
        // it from the right. Template checks keep their original visit order.
        write := len(types)
        i := len(types)""").replace("types = slices.Delete(types, i, i+1)", """continue
            }
            write--
            if write != i {
                types[write] = t""").replace("\n\t}\n\treturn types", """
        if write != 0 {
            kept := copy(types, types[write:])
            clear(types[kept:])
            return types[:kept]
        }
    }
    return types""")
assert body.count("clear(types[kept:])")==1 and "slices.Delete" not in body
target = out / "checker.go"
target.write_text(control[:start]+body+control[end:])
(out/"overlay.json").write_text(json.dumps({"Replace":{str(root/path):str(target)}}))
