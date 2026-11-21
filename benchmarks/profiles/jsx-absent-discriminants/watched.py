"""Generate the write-invalidated variant of the grouped narrowing experiment."""
from pathlib import Path
import difflib
import hashlib
import json
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]/"packages/tsc-go"
out = Path(sys.argv[1]).resolve()
subprocess.run([sys.executable,here/"groups.py",out,"--linked"],check=True)
files = json.loads((out/"overlay.json").read_text())["Replace"]
inventory = json.loads((here/"value-writes.json").read_text())
for name, digest in inventory["files"].items():
    path = root/"internal/checker"/name
    src = path.read_bytes()
    assert hashlib.sha256(src).hexdigest() == digest
    dest = out/name
    current = dest.read_bytes() if str(path) in files else src
    # Locate stores by exact line blocks, preserving earlier overlay edits.
    src_lines = src.splitlines(keepends=True)
    current_lines = current.splitlines(keepends=True)
    edits = []
    offsets = [0]
    for line in src_lines:
        offsets.append(offsets[-1]+len(line))
    current_offsets = [0]
    for line in current_lines:
        current_offsets.append(current_offsets[-1]+len(line))
    for block in difflib.SequenceMatcher(a=src_lines,b=current_lines,autojunk=False).get_matching_blocks():
        lo, hi = offsets[block.a], offsets[block.a+block.size]
        for w in inventory["writes"]:
            if w["File"]!=name or not lo <= w["Start"] < w["End"] <= hi: continue
            offset = current_offsets[block.b]-lo
            a,b = w["Start"]+offset,w["End"]+offset
            assert current[a:b]==src[w["Start"]:w["End"]]
            replacement=f'{w["Checker"]}.setResolvedValue({w["Receiver"]}, {w["Value"]})'
            edits.append((a,b,replacement.encode()))
    assert len(edits)==sum(w["File"]==name for w in inventory["writes"])
    for a,b,r in sorted(edits,reverse=True):
        current=current[:a]+r+current[b:]
    dest.write_bytes(current)
    files[str(path)] = str(dest)
path=root/"internal/checker/types.go"
s=path.read_text()
site="functionOrConstructorChecked bool"
assert s.count(site)==1
(out/"types.go").write_text(s.replace(site,site+"\n    watchesAbsentProperties bool"))
files[str(path)]=str(out/"types.go")
path=root/"internal/checker/absent_groups.go"
s=Path(files[str(path)]).read_text()
a=s.index("type mappedPropertyWitness struct")
b=s.index("type absentPropertyPlan struct")
s=s[:a]+"""type absentPropertySpan struct { start,end int }

func (c *Checker) setResolvedValue(links *ValueSymbolLinks, value *Type) {
    if links.watchesAbsentProperties && links.resolvedType != value {
        clear(c.absentPlans)
        links.watchesAbsentProperties = false
    }
    links.resolvedType = value
}

"""+s[b:]
a=s.index("var witnesses ")
b=s.index("return plan\n}",a)
s=s[:a]+"""start := 0
    for i, member := range members {
        all := true
        for _,t := range types {
            prop := t.AsIntersectionType().propertyCacheWithoutFunctionPropertyAugment[member.Name]
            if !mappedLookupReadsResolvedType(prop) { all = false; break }
            links := c.valueSymbolLinks.TryGet(prop)
            if links == nil || links.resolvedType == nil { all = false; break }
            value := links.resolvedType
            if value != c.undefinedType && !(value.flags&TypeFlagsUnion != 0 && containsType(value.Types(),c.undefinedType)) {
                all=false
                break
            }
            links.watchesAbsentProperties = true
        }
        if !all {
            if start<i { plan.spans=append(plan.spans,absentPropertySpan{start,i}) }
            start=i+1
        }
    }
    if start<len(members) { plan.spans=append(plan.spans,absentPropertySpan{start,len(members)}) }
    """+s[b:]
a=s.index("// The non-augmented")
b=s.index("func (c *Checker) validLinkedSpan",a)
s=s[:a]+"// Property and value replacements invalidate every pending span.\n"+s[b:]
a=s.index("for _, w := range span.witnesses")
b=s.index("return true",a)
s=s[:a]+s[b:]
(out/"watched_groups.go").write_text(s)
files[str(path)]=str(out/"watched_groups.go")
(out/"overlay.json").write_text(json.dumps({"Replace":files}))
path=out/"linked_test.go"
s=path.read_text()
import re
s,n = re.subn(r'c\.valueSymbolLinks.Get\((cache\["\w+"\])\)\.resolvedType = (.+)',r'c.setResolvedValue(c.valueSymbolLinks.Get(\1), \2)',s)
assert n==4
site='c.publishLookupProperty(cache, "first", replacement, true)'
s=s.replace(site,'''plan = c.makeAbsentPropertyPlan(target.Types(), members)
    c.absentPlans[target] = plan
    '''+site)
path.write_text(s)
files[str(root/"internal/checker/absent_groups_test.go")]=str(path)
files[str(root/"internal/checker/absent_midpass_test.go")]=str(here/"watched_test.go.txt")
(out/"test-overlay.json").write_text(json.dumps({"Replace":files}))
