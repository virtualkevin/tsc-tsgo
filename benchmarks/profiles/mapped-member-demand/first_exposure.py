"""Add first-container caller attribution to the existing mapped-member probe."""
import json
from pathlib import Path
import subprocess
import sys

here=Path(__file__).resolve().parent
out=Path(sys.argv[1]).resolve()
subprocess.run([sys.executable,here/"prepare.py",out],check=True)
config=out/"overlay.json"
overlay=json.loads(config.read_text())
source=(here/"probe.go.txt").read_text().replace('"sync"', '"sync"\n "runtime"\n "strings"\n "strconv"')
source=source.replace('flags atomic.Uint32\n    entries','first sync.Once\n    caller string\n    flags atomic.Uint32\n    entries',1)
source+='''
func (owner *mappedDemandOwner) expose(flag uint32) {
    owner.flags.Or(flag)
    owner.first.Do(func(){
        var pcs [12]uintptr
        n:=runtime.Callers(2,pcs[:])
        frames:=runtime.CallersFrames(pcs[:n])
        var path []string
        started:=false
        for {
            f,more:=frames.Next()
            name:=strings.TrimPrefix(f.Function,"github.com/microsoft/typescript-go/internal/checker.")
            if started && len(path)<4 {
                path=append(path,name+"@"+strconv.Itoa(f.Line))
            }
            if name=="(*StructuredType).Properties" || name=="(*StructuredType).Members" {
                started=true
                path=append(path,name)
            }
            if !more || len(path)>=4 {break}
        }
        if !started {panic("missing container accessor frame")}
        owner.caller=strings.Join(path," / ")
    })
}
'''
source=source.replace('Cohorts [3][16]uint64','First map[string][3]uint64\n    Cohorts [3][16]uint64')
source=source.replace('var out MappedDemandReport','var out MappedDemandReport\n out.First=make(map[string][3]uint64)\n owners:=make(map[*mappedDemandOwner]bool)')
source=source.replace('out.Cohorts[entry.cohort][mask]++','''out.Cohorts[entry.cohort][mask]++
            site:=entry.owner.caller
            if site=="" {site="(no container exposure)"}
            counts:=out.First[site]
            if !owners[entry.owner] {owners[entry.owner]=true; counts[0]++}
            counts[1]++
            if mask&3==0 {counts[2]++}
            out.First[site]=counts''')
dest=out/"first.go"
dest.write_text(source)
key,= [k for k in overlay["Replace"] if k.endswith("/mapped_demand_probe.go")]
overlay["Replace"][key]=str(dest)
path=out/"types.go"
source=path.read_text()
assert source.count("owner.flags.Or(")==2
path.write_text(source.replace("owner.flags.Or(","owner.expose("))
config.write_text(json.dumps(overlay))
