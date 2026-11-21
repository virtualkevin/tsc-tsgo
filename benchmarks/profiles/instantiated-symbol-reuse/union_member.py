"""Identify the generic member of the dominant two-arm Sentry union."""
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
out = Path(sys.argv[1]).resolve()
subprocess.run([sys.executable, here/"union_shape.py", out], check=True)
p = out/"checker.go"
s = p.read_text().replace("var param, concrete, other int", "var param, concrete, other int\n            var atom, member *Type")
s = s.replace("concrete++", "concrete++; atom=arm").replace("default: other++", "default: other++; member=arm")
start = s.index("label:=fmt.Sprintf(")
end = s.index("value,_ :=", start)
s = s[:start]+'''if param==0 && concrete==1 && other==1 && source==t && t.alias==nil && c.findActiveMapper(key.mapper)<0 {
            label:=fmt.Sprintf("atom=%v member=%s nested=%d",atom.flags,describeUnionMember(member),work)
            '''+s[end:]
s = s.replace("if result == key.input {row[4].Add(1)}", "if result == key.input {row[4].Add(1)}\n            }")
s += """
func describeUnionMember(t *Type) string {
    alias:=""
    if t.alias!=nil && t.alias.symbol!=nil {alias=t.alias.symbol.Name}
    ref:=""
    if t.flags&TypeFlagsObject!=0 && t.objectFlags&ObjectFlagsReference!=0 {
        target:=t.Target()
        if target!=nil && target.symbol!=nil {ref=target.symbol.Name}
    }
    return fmt.Sprintf("%v alias=%s ref=%s",t.flags,alias,ref)
}
"""
p.write_text(s)
