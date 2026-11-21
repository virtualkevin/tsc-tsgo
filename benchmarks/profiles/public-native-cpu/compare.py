"""Compare inclusive samples at corresponding compiler operations in the two native profiles."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
public = json.loads((here/"summary.json").read_text())["projects"]
go = json.loads((here/"go.json").read_text())["projects"]
# The TS implementation dispatches from a normal-mode wrapper to the mode-aware BodyEx.
methods = dict.fromkeys(("getResolvedSignature", "isSignatureApplicable", "getTypeOfSymbol",
    "checkExpressionWithContextualType", "checkObjectLiteral", "checkPropertyAssignment",
    "createJsxAttributesTypeFromAttributesProperty", "instantiateTypeWithAlias",
    "isRelatedToEx", "getPropertyOfTypeEx", "getUnionTypeWorker"))
methods["getReturnTypeFromBody"] = "getReturnTypeFromBodyEx"
wanted = set(methods)
result = {}
for project, sample in go.items():
    assert sample["commit"] == public[project]["commit"]
    profile = here/(project+"-go.pb.gz")
    assert hashlib.sha256(profile.read_bytes()).hexdigest()==sample["cpuProfileSha256"]
    raw = subprocess.check_output([sys.argv[1],"tool","pprof","-raw",profile],text=True)
    samples, locations = raw.split("Locations\n", 1)
    frames = {}
    for line in locations.split("Mappings\n")[0].splitlines():
        match = re.match(r"^\s*(\d+):\s+0x[\da-f]+(?: M=\d+)?\s+(.*)", line)
        if match:
            slot = frames[int(match[1])] = set()
            line = match[2]
        method = re.search(r"internal/checker\.\(\*(?:Checker|Relater)\)\.(\w+)\s",line)
        if re.search(r"runtime\.(gcDrain\w*|gcAssistAlloc\w*|scanObject|gcBgMarkWorker)\s",line):
            slot.add("<gc-mark>")
        if method and method[1] in wanted:
            slot.add(method[1])
    inclusive = Counter()
    total = 0
    for ns,stack in re.findall(r"^\s*\d+\s+(\d+):\s*([\d ]+)$",samples,re.M):
        total += int(ns)
        for name in set().union(*(frames[int(i)] for i in stack.split())):
            inclusive[name] += int(ns)
    table = gzip.decompress((here/(project+"-functions.txt.gz")).read_bytes())
    assert hashlib.sha256(table).hexdigest()==public[project]["tableSha256"]
    symbols = re.findall(r"^\s*[\d.]+\s+[\d.]+\s+([\d.]+)\s+[\d.]+\s+(sc_bf_\S+)$",table.decode(),re.M)
    comparison = {}
    for name,peer in methods.items():
        target = peer or name
        matched = [(float(ns),sym) for ns,sym in symbols if re.search("_"+target+r"(?:\.i32)?$",sym)]
        if len(matched)!=1 or not inclusive[name]:
            continue
        seconds,symbol = matched[0]
        comparison[name] = dict(publicSymbol=symbol,publicInclusiveCPUSeconds=seconds,goInclusiveCPUSeconds=inclusive[name]/1e9)
    result[project] = dict(publicSampledCPUSeconds=public[project]["sampledCPUSeconds"],goSampledCPUSeconds=total/1e9,
        goMarkAndAssistCPUSeconds=inclusive["<gc-mark>"]/1e9,methods=comparison)
(here/"comparison.json").write_text(json.dumps(result,indent=2)+"\n")
