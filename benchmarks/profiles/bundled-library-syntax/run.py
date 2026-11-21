"""Run the library metadata check and in-memory parse/decode benchmark."""
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
overlay = out / "library-overlay.json"
overlay.write_text(json.dumps({"Replace": {
    str(root / "internal/api/encoder/library_test.go"): str(here / "library_test.go.txt")
}}))
ref = json.loads(gzip.decompress((here.parent / "public-npm/0.0.2.json.gz").read_bytes()))
env = dict(os.environ, TSC_LIBRARY_RESULT=str(here / "roundtrip.json"))
env.update(ref["environment"]["compilerEnvironment"])
subprocess.run([sys.argv[2], "test", "-count=3", "-overlay=" + str(overlay), "-run", "^TestLibraryRepresentation$",
                "-bench", "^BenchmarkLibraryFrontEnd$", "-benchtime=300ms", "./internal/api/encoder"],
               env=env, cwd=root, stdout=(out / "library-bench.txt").open("w"), check=True)
