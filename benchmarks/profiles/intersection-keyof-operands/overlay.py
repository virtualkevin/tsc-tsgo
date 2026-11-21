"""Split the existing keyof observer at the boundary to union construction."""
from pathlib import Path
import subprocess
import sys

here=Path(__file__).resolve().parent
out=Path(sys.argv[1]).resolve()
subprocess.run([sys.executable,here.parent/"intersection-keyof-reuse/overlay.py",out],check=True)
p=out/"checker.go"
s=p.read_text()
site="result := c.getUnionType(core.Map(t.Types(), func(t *Type) *Type { return c.getIndexTypeEx(t, indexFlags) }))"
assert s.count(site)==1
s=s.replace("first *Type\n    active int","first *Type\n    operands []*Type\n    active int")
s=s.replace("keyofCounts [7]","keyofCounts [15]")
s=s.replace(site,"""operands := core.Map(t.Types(), func(t *Type) *Type { return c.getIndexTypeEx(t, indexFlags) })
        afterOperands := c.TotalInstantiationCount
        result := c.getUnionType(operands)
        if prior != nil {
            if before != afterOperands { keyofCounts[7].Add(1) }
            if afterOperands != c.TotalInstantiationCount { keyofCounts[8].Add(1) }
            if slices.Equal(operands, entry.operands) {
                keyofCounts[9].Add(1)
                if len(operands)==2 && (operands[0].flags|operands[1].flags)&TypeFlagsUnion != 0 {
                    keyofCounts[10].Add(1)
                } else {
                    keyofCounts[11].Add(1)
                    if len(operands)==2 { keyofCounts[12].Add(1) }
                    if result != prior { keyofCounts[13].Add(1) }
                    if afterOperands != c.TotalInstantiationCount { keyofCounts[14].Add(1) }
                }
            }
        } else if entry.first == nil {
            entry.operands = slices.Clone(operands)
        }""")
p.write_text(s)
