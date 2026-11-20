"""Request transparent huge pages on Go heap mappings in an isolated Linux build."""
import json
from pathlib import Path
import sys

goroot, output = (Path(arg).resolve() for arg in sys.argv[1:])
source = goroot / "src/runtime/mem_linux.go"
anchor = "if debug.disablethp != 0 {\n\t\tsysNoHugePageOS(v, n)\n\t}"
original = source.read_text()
assert original.count(anchor) == 1
updated = original.replace(anchor, anchor[:-1] + ' } else if vmaName == "heap" {\n\t\tsysHugePageOS(v, n)\n\t}')
output.mkdir(exist_ok=True)
target = output / source.name
target.write_text(updated)
(output / "overlay.json").write_text(json.dumps({"Replace": {str(source): str(target)}}))
