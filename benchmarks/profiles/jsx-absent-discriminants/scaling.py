"""Compare JSX absent-member scaling, diagnostics and declaration output."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
names = ("public", "control", "candidate")
bins = dict(zip(names, (Path(x).absolute() for x in sys.argv[1:]), strict=True))
env = {k: v for k, v in os.environ.items() if not k.startswith(("TSC_", "SCRIPTC_", "TS_GO_"))}
env["TSC_TS_LIB_DIR"] = str(root / "upstream/typescript-go/internal/bundled/libs")
flags = ["--strict", "--skipLibCheck", "--jsx", "preserve", "--pretty", "false"]
def sha(data):
    return hashlib.sha256(data).hexdigest()

def program(width, error):
    # Each absent k property discriminates optional vs required variants.
    variants = []
    for i in range(32):
        optional = "?" if i % 2 == 0 else ""
        fields = " ".join(f"k{j}{optional}: {i};" for j in range(32))
        variants.append("{ " + fields + (' value: string }' if optional else ' value: number }'))
    values = ['<box value="ok" />'] * width
    if error:
        values += ['<box value={17} />']
    return ("declare global { namespace JSX { interface Element {} interface IntrinsicElements { box: " +
            " | ".join(variants) + " } } }\nexport const values = [\n" +
            ",\n".join(values) + "\n];\n")

def invoke(engine, args, cwd):
    start = time.perf_counter_ns()
    run = subprocess.run([bins[engine], *flags, *args, "case.tsx"], cwd=cwd, env=env, capture_output=True, timeout=180)
    return run, (time.perf_counter_ns() - start) / 1_000_000

report = {"flags": flags, "binaries": {k: sha(v.read_bytes()) for k,v in bins.items()}, "widths": {}}
with tempfile.TemporaryDirectory() as work:
    work = Path(work)
    for width in (16, 256, 1024):
        case = work / "case.tsx"
        case.write_text(program(width, False))
        row = {"sourceSha256": sha(case.read_bytes()), "rounds": [], "correctness": {}}
        for order in (names, names[1:] + names[:1], names[2:] + names[:2]):
            times = {}
            for engine in order:
                r, times[engine] = invoke(engine, ["--noEmit"], work)
                assert (r.returncode, r.stdout, r.stderr) == (0,b"",b""), (engine,r.stdout,r.stderr)
            row["rounds"].append(times)
        for error in (False, True):
            case.write_text(program(width, error))
            reference = None
            for engine in names:
                dest = work / (engine + str(width) + str(error))
                r, _ = invoke(engine, ["--declaration", "--emitDeclarationOnly", "--outDir", str(dest)], work)
                result = (r.returncode, r.stdout, r.stderr, (dest / "case.d.ts").read_bytes())
                if reference is None:
                    reference = result
                assert result == reference, (width, error, engine, r.stdout, r.stderr)
                assert (r.returncode != 0) == error and bool(r.stdout) == error and not r.stderr
            row["correctness"][str(error)] = {"exit": reference[0], "diagnosticsSha256": sha(reference[1]),
                                             "declarationSha256": sha(reference[3])}
        report["widths"][width] = row
        print(width, row, flush=True)
(here / "scaling.json").write_text(json.dumps(report, indent=2) + "\n")
