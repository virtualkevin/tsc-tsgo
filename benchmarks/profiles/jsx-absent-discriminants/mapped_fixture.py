"""Confirm the generated mapped fixture exercises the resolved property checks."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
sys.dont_write_bytecode = True
import scaling

binary = Path(sys.argv[1]).resolve()
widths = {}
with tempfile.TemporaryDirectory() as tmp:
    cwd = Path(tmp)
    for n in (1, 16, 256, 1024):
        source = scaling.program(n, False, True).encode()
        (cwd/"case.tsx").write_bytes(source)
        scaling.bins = {"observer": binary}
        run, _ = scaling.invoke("observer",["--noEmit"],cwd)
        assert run.returncode == 0 and not run.stdout
        counts = json.loads(run.stderr)
        widths[n] = {"sourceSha256":scaling.sha(source), **counts}
        print(n, counts["cells"][7],flush=True)
result = {"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"widths":widths}
(scaling.here/"mapped-fixture.json").write_text(json.dumps(result,indent=2)+"\n")
