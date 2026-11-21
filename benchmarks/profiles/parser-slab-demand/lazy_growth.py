"""Stage per-kind lazy growth without reserving a mixed slab at file entry."""
from pathlib import Path
import json
import subprocess
import sys

here=Path(__file__).resolve().parent
root=here.parents[2]/"packages/tsc-go"
out=Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
policy=json.loads((here/"growth.json").read_text())["all projects"]["policy"]
files={}
for name in ("internal/core/arena.go","internal/ast/ast.go","internal/ast/ast_generated.go"):
    text=subprocess.check_output(["git","show","50291d2:packages/tsc-go/"+name],cwd=root,text=True)
    if name=="internal/core/arena.go":
        start=text.index("func (a *Arena[T]) New()")
        end=text.index("\n}",start)+2
        new=text[start:end].replace("New()","NewWithGrowth(first, limit int)").replace("nextSize := nextArenaSize(len(a.data))","nextSize := min(max(first, 2*len(a.data)), limit)")
        text=text[:end]+"\n\n// NewWithGrowth uses a caller-selected first page and growth cap.\n"+new+text[end:]
    else:
        for typ,(first,limit) in policy.items():
            field=typ[0].lower()+typ[1:]
            field=field.replace("jSDoc","jsdoc")
            orig=f"f.{field}Arena.New()"
            if name.endswith("ast_generated.go"):
                assert text.count(orig)==(0 if typ=="NodeList" else 1), typ
            else:
                assert text.count(orig)==(1 if typ=="NodeList" else 0), typ
            text=text.replace(orig,f"f.{field}Arena.NewWithGrowth({first}, {limit})")
    dest=out/Path(name).name
    dest.write_text(text)
    files[str(root/name)]=str(dest)
(out/"overlay.json").write_text(json.dumps({"Replace":files}))
