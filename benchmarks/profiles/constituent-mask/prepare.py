"""Build a word-sized survivor mask experiment through a Go overlay."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
source = root / "internal/checker/relater.go"
entry = "func (c *Checker) discriminateTypeByDiscriminableItems(target *Type, discriminator Discriminator) *Type {"
code = source.read_text()
assert code.count(entry) == 1
patched = out / "relater.go"
patched.write_text(code.replace(entry, entry + "\n if len(target.Types()) <= 64 { return c.discriminateWithMask(target, discriminator) }"))
overlay = out / "overlay.json"
overlay.write_text(json.dumps({"Replace": {str(source): str(patched), str(source.with_name("constituent_mask.go")): str(here / "mask.go.txt")}}))
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay=" + str(overlay), "-o", out/"tsgo", "./cmd/tsgo"], cwd=root, check=True)
