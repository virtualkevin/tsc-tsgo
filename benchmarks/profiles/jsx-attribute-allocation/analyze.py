"""Attribute each sampled Sentry allocation or CPU tick inside attribute checking once."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
groups = here.parent / "reduction-group-index"
native = here.parent / "public-native-cpu"
signature = "github.com/microsoft/typescript-go/internal/checker.(*Checker)."
builder = signature + "createJsxAttributesTypeFromAttributesProperty"
attr = signature + "checkJsxAttribute"
mutable = signature + "checkExpressionForMutableLocation"
def read_json(path):
    return json.loads(path.read_text())

def analyze(path, sha, heap):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == sha
    raw = subprocess.check_output([sys.argv[1], "tool", "pprof", "-raw", path], text=True)
    samples, locations = raw.split("Locations\n", 1)
    frames = {}
    for line in locations.split("Mappings\n")[0].splitlines():
        loc = re.match(r"^\s*(\d+):\s+0x[\da-f]+(?: M=\d+)?\s+(.*)", line)
        if loc:
            slot = frames[int(loc[1])] = []
            line = loc[2]
        frame = re.fullmatch(r"\s*(.+?) (\S+):(\d+):\d+(?: s=\d+.*)?", line)
        if frame:
            slot.append((frame[1], int(frame[3])))
    branch, stages, consumers, sites = (Counter() for _ in range(4))
    mapping = Counter()
    total = 0
    pattern = r"^\s*\d+\s+(\d+)\s+\d+\s+\d+:\s*([\d ]+)$" if heap else r"^\s*\d+\s+(\d+):\s*([\d ]+)$"
    for value, stack in re.findall(pattern, samples, re.M):
        weight = int(value)
        if not weight:
            continue
        total += weight
        ids = stack.split()
        entries = [frame for loc in ids for frame in frames[int(loc)]]
        names = [f for f,_ in entries]
        mapper = signature+"mapTypeEx"
        if mapper in names:
            i = names.index(mapper)
            callers = [f for f in names[i+1:] if f.startswith(signature) and f not in (mapper,signature+"mapType")]
            origin = callers[0].removeprefix(signature) if callers else "<other>"
            line = entries[i][1]
            mapping[origin,line] += weight
        # Charge to the innermost builder, using the expression call at jsx.go:740.
        if builder not in names:
            continue
        owner = names.index(builder)
        if owner == 0 or names[owner-1] != attr:
            continue
        chain = names[:owner][::-1]
        key = "<outside mutable location>"
        if mutable in chain:
            i = chain.index(mutable)+1
            key = chain[i].removeprefix(signature) if i<len(chain) else "<local>"
        branch[key] += weight
        stage = next((f.removeprefix(signature) for f in chain if f.startswith(signature) and
                      ("discriminate" in f.split(".")[-1].lower() or f.endswith((".getTypeOfPropertyOfContextualType",".getContextualTypeForChildJsxExpression")))), "<other>")
        stages[key,stage] += weight
        consumer = next((f.removeprefix(signature) for f in chain if f.startswith(signature) and f.endswith((
            ".getUnionOrIntersectionProperty",".getSpreadType",".getUnionTypeWorker",".hasNeverReducedProperty",
            ".getResolvedSignature",".instantiateTypeWithAlias",".getTypeOfSymbol",".resolveStructuredTypeMembers"))), "<other>")
        consumers[key,stage,consumer] += weight
        site = frames[int(ids[0])]
        label = f"{site[0][0]}:{site[0][1]}" if site else "<unsymbolized>"
        sites[key,stage,label] += weight
    def rows(counter, labels):
        return [dict(zip(labels,k if isinstance(k,tuple) else (k,)), weight=v) for k,v in counter.most_common()]
    assert sum(branch.values()) == sum(stages.values()) == sum(consumers.values()) == sum(sites.values())
    return dict(total=total,attribute=sum(branch.values()),branches=dict(branch.most_common()),
                stages=rows(stages,("branch","stage")),consumers=rows(consumers,("branch","stage","consumer")),
                topSites=rows(sites,("branch","stage","site"))[:50],
                mappingCallers=rows(mapping,("caller","line"))[:40])

report = {}
for stem in ("", "sparse-"):
    ref = read_json(groups/(stem+"allocations.json"))["samples"]["control"]
    result = analyze(groups/(stem+"control-mem.pb.gz"),ref["profileSha256"],True)
    assert result["attribute"] == ref["jsxChildrenBytes"]["checkJsxAttribute"]
    report[stem+"controlBytes"] = result
cpu = read_json(native/"go.json")["projects"]["sentry"]
report["controlCPUNanoseconds"] = analyze(native/"sentry-go.pb.gz", cpu["cpuProfileSha256"],False)
public = gzip.decompress((native/"sentry-functions.txt.gz").read_bytes())
assert hashlib.sha256(public).hexdigest()==read_json(native/"summary.json")["projects"]["sentry"]["tableSha256"]
report["publicInclusiveCPUSeconds"] = {symbol:float(time) for time,symbol in re.findall(
    r"^\s*[\d.]+\s+[\d.]+\s+([\d.]+)\s+[\d.]+\s+(sc_bf_\S+)$",public.decode(),re.M)
    if re.search(r"_(checkJsxAttribute|discriminateContextualTypeByJSXAttributes|getContextualTypeForJsxAttribute|checkExpressionForMutableLocationEx)(?:\.i32)?$",symbol,re.I)}
(here/"results.json").write_text(json.dumps(report,indent=2)+"\n")
