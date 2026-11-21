"""Compare declarations and diagnostics on the mapped JSX union with optional properties."""
import json
from pathlib import Path
import runpy
import sys
import tempfile

here = Path(__file__).resolve().parent
shared = runpy.run_path(str(here.parent / "jsx-absent-discriminants/scaling.py"))
invoke = shared["invoke"]
invoke.__globals__["bins"] = dict(zip(shared["names"], sys.argv[1:], strict=True))
rows = []
with tempfile.TemporaryDirectory() as tmp:
    cwd = Path(tmp)
    for width in (1, 16, 256):
        for invalid in (False, True):
            source = shared["grouped_program"](width, invalid)
            (cwd/"case.tsx").write_text(source)
            expected = None
            for engine in shared["names"]:
                dest = cwd / f"{engine}-{width}-{invalid}"
                r, _ = invoke(engine, ["--declaration","--emitDeclarationOnly","--outDir",str(dest)], cwd)
                out = (r.returncode, r.stdout, r.stderr, (dest/"case.d.ts").read_bytes())
                if expected is None:
                    expected = out
                assert out == expected and bool(out[0]) == invalid and bool(out[1]) == invalid and not out[2]
            rows.append(dict(elements=width, invalid=invalid, exit=out[0], sourceSha256=shared["sha"](source.encode()),
                             diagnosticSha256=shared["sha"](out[1]), declarationSha256=shared["sha"](out[3])))
(here/"fixture.json").write_text(json.dumps(rows,indent=2)+"\n")
