"""Classify recomputed substitution hits by input and concrete mapper implementation."""
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
out = Path(sys.argv[1]).resolve()
subprocess.run([sys.executable, here/"prepare.py", out], check=True)
p = out / "checker.go"
s = p.read_text().replace("type observedResult struct {", "type observedResult struct {\n    work uint64")
s = s.replace("observedResult{owner, result}", "observedResult{work, owner, result}")
s = s.replace("counts[2].Add(1)", """if kind == 1 {
            label := observedClass(key.input, key.mapper)
            value,_ := observedClasses.LoadOrStore(label, &[5]atomic.Uint64{})
            row := value.(*[5]atomic.Uint64)
            row[0].Add(1)
            row[1].Add(work)
            if work != prev.work {row[2].Add(1)}
            if result != prev.result {row[3].Add(1)}
            if result == key.input {row[4].Add(1)}
        }
        counts[2].Add(1)""")
s += """
var observedClasses sync.Map
func observedClass(t *Type, m *TypeMapper) string {
    kind := "other"
    switch {
    case t.flags&TypeFlagsTypeParameter!=0: kind="parameter"
    case t.flags&TypeFlagsUnion!=0: kind="union"
    case t.flags&TypeFlagsIntersection!=0: kind="intersection"
    case t.flags&TypeFlagsIndexedAccess!=0: kind="indexedAccess"
    case t.flags&TypeFlagsConditional!=0: kind="conditional"
    case t.flags&TypeFlagsObject!=0:
        switch {
        case t.objectFlags&ObjectFlagsReference!=0: kind="reference"
        case t.objectFlags&ObjectFlagsMapped!=0: kind="mapped"
        case t.objectFlags&ObjectFlagsAnonymous!=0: kind="anonymous"
        default: kind="otherObject"
        }
    }
    if m==nil {return kind+"/nil"}
    switch v:=m.data.(type) {
    case *CompositeTypeMapper:
        return fmt.Sprintf("%s/composite(%T,%T)",kind,v.m1.data,v.m2.data)
    case *MergedTypeMapper:
        return fmt.Sprintf("%s/merged(%T,%T)",kind,v.m1.data,v.m2.data)
    }
    return fmt.Sprintf("%s/%T", kind, m.data)
}
func ObservedClasses() map[string][5]uint64 {
    rows:=map[string][5]uint64{}
    observedClasses.Range(func(k,v any) bool {
        var row [5]uint64
        for i:=range row {row[i]=v.(*[5]atomic.Uint64)[i].Load()}
        rows[k.(string)] = row
        return true
    })
    return rows
}
"""
p.write_text(s)
p = out / "main.go"
p.write_text(p.read_text().replace("checker.ObservedSubstitutions()", "checker.ObservedClasses()"))
