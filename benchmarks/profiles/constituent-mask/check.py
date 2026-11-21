"""Compare public and Go results at the word boundary, with errors and declaration emit."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
env = {k: v for k, v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env["TSC_TS_LIB_DIR"] = str(here.parents[2] / "upstream/typescript-go/internal/bundled/libs")
engines = dict(zip(("public", "go", "candidate"), sys.argv[1:], strict=True))
rows = []
with tempfile.TemporaryDirectory() as tmp:
    work = Path(tmp)
    for width in (2, 63, 64, 65):
        branches = [f'{{ kind: "v{i}"; value: {i}; optional?: {i} }}' for i in range(width)]
        base = "declare global { namespace JSX { interface Element {} interface IntrinsicElements { box: " + " | ".join(branches) + " } } }\n"
        base += f'const last = {{kind: "v{width-1}", value: {width-1}}} as const;\n'
        base += 'export const rows = [<box kind="v0" value={0} />, <box {...last} />];\n'
        errors = ['<box kind="other" value={0} />', '<box value={0} />', '<box kind="v0" value={1} />']
        for invalid in (False, True):
            source = base + ('export const bad = [' + ','.join(errors) + '];\n' if invalid else '')
            (work / 'case.tsx').write_text(source)
            expected = None
            for engine, binary in engines.items():
                dest = work / f"{engine}-{width}-{invalid}"
                r = subprocess.run([binary, "--strict", "--skipLibCheck", "--jsx", "preserve", "--pretty", "false",
                                    "--declaration", "--emitDeclarationOnly", "--outDir", dest, "case.tsx"],
                                   env=env, cwd=work, capture_output=True, timeout=60)
                actual = (r.returncode, r.stdout, r.stderr, (dest / "case.d.ts").read_bytes())
                if expected is None:
                    expected = actual
                assert actual == expected and bool(r.returncode) == invalid and not r.stderr, (width, engine, r.stdout)
            rows.append({"width": width, "invalid": invalid, "exit": expected[0],
                         "diagnosticsSha256": hashlib.sha256(expected[1]).hexdigest(),
                         "declarationSha256": hashlib.sha256(expected[3]).hexdigest()})
(here / "checks.json").write_text(json.dumps(rows, indent=2) + "\n")
