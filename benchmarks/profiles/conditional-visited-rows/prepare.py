"""Stage exact inference-state rows for wide object/conditional comparisons."""
import json
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[3]
path=Path("packages/tsc-go/internal/checker/inference.go")
s=subprocess.check_output(["git","show",f"8d9a8c3:{path}"],cwd=root,text=True)
def replace(old,new):
    global s
    assert s.count(old)==1,old
    s=s.replace(old,new)
replace("type InferenceState struct {","""// A zero slot is empty. Stored priorities range from Circularity (-1) to
// MaxValue, with two added so a recorded zero priority is distinguishable.
type conditionalVisitRow struct {
	columns map[TypeId]int
	status []InferencePriority
}

type InferenceState struct {
	conditionalRows map[TypeId]*conditionalVisitRow""")
replace("matched := make([]bool, len(sources))","matched := make([]bool, len(sources))\n var columns map[TypeId]int")
site="for i := range sources {\n\t\t\t\t\tsaveInferencePriority"
replace(site,"""if len(sources)>=32 && t.flags&TypeFlagsConditional!=0 && n.conditionalRows[t.id]==nil {
                    if columns==nil {
                        columns=make(map[TypeId]int,len(sources))
                        for i,s:=range sources { if s.flags&TypeFlagsObject!=0 {columns[s.id]=i} }
                    }
                    if len(columns)>=32 {
                        if n.conditionalRows==nil { n.conditionalRows=make(map[TypeId]*conditionalVisitRow) }
                        n.conditionalRows[t.id]=&conditionalVisitRow{columns:columns,status:make([]InferencePriority,len(sources))}
                    }
                }
                """+site)
old="""if status, ok := n.visited[key]; ok {
		n.inferencePriority = min(n.inferencePriority, status)
		return
	}
	if n.visited == nil {
		n.visited = make(map[InferenceKey]InferencePriority)
	}
	n.visited[key] = InferencePriorityCircularity"""
replace(old,"""var slot *InferencePriority
	if n.conditionalRows != nil && target.flags&TypeFlagsConditional != 0 {
		if row:=n.conditionalRows[target.id]; row!=nil {
			if col,ok:=row.columns[source.id];ok {
				slot=&row.status[col]
				if *slot!=0 {
					n.inferencePriority=min(n.inferencePriority,*slot-2)
					return
				}
			}
		}
	}
	// The pair may have entered the general table before a row existed.
	if status,ok:=n.visited[key];ok {
		n.inferencePriority=min(n.inferencePriority,status)
		return
	}
	if slot!=nil {
		*slot=InferencePriorityCircularity+2
	} else {
		if n.visited==nil { n.visited=make(map[InferenceKey]InferencePriority) }
		n.visited[key]=InferencePriorityCircularity
	}""")
replace("n.visited[key] = n.inferencePriority","if slot!=nil { *slot=n.inferencePriority+2 } else { n.visited[key]=n.inferencePriority }")
out=Path(sys.argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
f=out/path.name
f.write_text(s)
(out/"overlay.json").write_text(json.dumps({"Replace":{str(root/path):str(f)}}))
