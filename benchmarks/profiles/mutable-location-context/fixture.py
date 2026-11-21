"""Count the widening lookups added by each additional JSX string attribute."""
import json
from pathlib import Path
import sys
import tempfile

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / "jsx-absent-discriminants"))
sys.dont_write_bytecode = True
import scaling

binary = Path(sys.argv[1]).resolve()
quoted = "--quoted-jsx" in sys.argv
scaling.bins = {"observer": binary}
report = {"binarySha256":scaling.sha(binary.read_bytes()), "widths":{}}
with tempfile.TemporaryDirectory() as tmp:
    cwd = Path(tmp)
    for width in (1,16,256,1024):
        source = scaling.grouped_program(width, False).encode()
        (cwd/"case.tsx").write_bytes(source)
        run, _ = scaling.invoke("observer", ["--noEmit"], cwd)
        assert run.returncode == 0 and not run.stdout
        counts = json.loads(run.stderr)
        assert counts == [width if quoted else 2*width, width, 0, 0, 0, 0, 0, 0, 0]
        report["widths"][width] = {"sourceSha256":scaling.sha(source), "counters":counts}
        print(width,counts)
(here/("quoted-fixture.json" if quoted else "fixture.json")).write_text(json.dumps(report,indent=2)+"\n")
