"""Use heap page advice once Go has enabled huge pages for heap metadata."""
import json
from pathlib import Path
import re
import sys

goroot, out = (Path(s).resolve() for s in sys.argv[1:])
runtime = goroot / "src/runtime"
heap = (runtime / "mheap.go").read_text()
grow = heap.split("func (h *mheap) grow(",1)[1].split("\n}",1)[0]
# All heap-tagged mappings read arenasHugePages while the heap lock is held.
calls = re.findall(r'\bsysMap\([^\n]+"heap"\)', grow)
assert len(calls) == 2 and "assertLockHeld(&h.lock)" in grow
all_calls = [line.strip() for p in runtime.glob("*.go") for line in p.read_text().splitlines()
             if 'sysMap(' in line and '"heap"' in line]
assert sorted(all_calls) == sorted(calls)
source = runtime / "mem_linux.go"
before = source.read_text()
anchor = "if debug.disablethp != 0 {\n\t\tsysNoHugePageOS(v, n)\n\t}"
assert before.count(anchor) == 1
after = before.replace(anchor, anchor + ' else if vmaName == "heap" && mheap_.arenasHugePages {\n\t\tsysHugePageOS(v, n)\n\t}')
out.mkdir(exist_ok=True)
patch = out / source.name
patch.write_text(after)
(out / "overlay.json").write_text(json.dumps({"Replace":{str(source):str(patch)}}))
