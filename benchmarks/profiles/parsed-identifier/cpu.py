"""Partition existing Go CPU samples within the innermost parser identifier call."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
prior = here.parent/"public-native-cpu"
baseline = json.loads((prior/"go.json").read_text())
result = {}
for project, ref in baseline["projects"].items():
    path = prior/(project+"-go.pb.gz")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == ref["cpuProfileSha256"]
    raw = subprocess.check_output([sys.argv[1],"tool","pprof","-raw",path],text=True)
    samples, locations = raw.split("Locations\n",1)
    assert "cpu/nanoseconds" in samples
    frames = {}
    for line in locations.split("Mappings\n")[0].splitlines():
        loc = re.match(r"^\s*(\d+):\s+0x[\da-f]+(?: M=\d+)?\s+(.*)",line)
        if loc:
            slot = frames[int(loc[1])] = []
            line = loc[2]
        frame = re.fullmatch(r"\s*(.+?) (\S+):(\d+):\d+(?: s=\d+.*)?",line)
        if frame:
            slot.append(frame[1])
    owner = "github.com/microsoft/typescript-go/internal/parser.(*Parser).createIdentifierWithDiagnostic"
    children = Counter()
    construction = Counter()
    factory = Counter()
    allocator = Counter()
    parse = 0
    factory_prefix = "github.com/microsoft/typescript-go/internal/ast.(*NodeFactory).New"
    total = 0
    for weight,stack in re.findall(r"^\s*\d+\s+(\d+):\s*([\d ]+)$",samples,re.M):
        weight = int(weight)
        total += weight
        chain = [f for i in stack.split() for f in frames[int(i)]]
        if "github.com/microsoft/typescript-go/internal/parser.ParseSourceFile" in chain:
            parse += weight
            entry = next((f for f in chain if f.startswith(factory_prefix)), None)
            if entry:
                kind = entry.removeprefix(factory_prefix)
                factory[kind] += weight
                if any(f.startswith(("runtime.mallocgc", "runtime.growslice", "runtime.makeslice")) for f in chain):
                    allocator[kind] += weight
        if owner not in chain:
            continue
        i = chain.index(owner)
        child = chain[i-1].split(".")[-1] if i else "<local>"
        children[child] += weight
        if child in ("newIdentifier","finishNode"):
            construction[chain[0]] += weight
    result[project] = dict(sha256=ref["cpuProfileSha256"],totalNs=total,identifierNs=children.total(),
                           immediateChildNs=dict(children.most_common()),factoryAndFinishLeafNs=dict(construction.most_common()),
                           parseSourceFileNs=parse, parserFactoryNs=dict(factory.most_common()),
                           parserFactoryWithAllocationNs=dict(allocator.most_common()))
(here/"cpu.json").write_text(json.dumps(result,indent=2)+"\n")
for project,r in result.items():
    print(project,r["totalNs"]/1e9, r["immediateChildNs"])
