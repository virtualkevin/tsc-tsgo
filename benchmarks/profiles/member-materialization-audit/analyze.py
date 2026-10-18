"""Reproduce a narrow source/profile selection audit; no new workload timing."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
report_path=root/'benchmarks/profiles/normal-map-attribution/report.json'
data=json.loads(report_path.read_text())
needles=['.(*pendingInstantiatedMembers).ownTable','.(*pendingInstantiatedMembers).keepTableOnDemand','.(*Checker).addInheritedMembers','.(*Checker).getNamedMembers']
rows=[]
for project in data['projects']:
 selected=[x for x in project['callers'] if any(x['name'].endswith(n) for n in needles)]
 assert len({x['name'] for x in selected})==len(selected)
 total=sum(x['cpuNs'] for x in selected)
 assert 0<=total<=project['mapPathCpuNs']<=project['totalCpuNs']
 rows.append({'project':project['project'],'totalCpuNs':project['totalCpuNs'],'selectedMapPathCpuNs':total,'selectedMapPathPercent':100*total/project['totalCpuNs'],'callers':[{'name':x['name'],'cpuNs':x['cpuNs']} for x in selected]})
inputs=[report_path,root/'packages/tsc-go/internal/checker/pending_members.go',root/'packages/tsc-go/internal/checker/checker.go',root/'benchmarks/profiles/pending-member-index/README.md']
report={'scope':'Offline selection from nearest-project-map-caller attribution, not all materialization CPU, allocation lifetime, removable work, or performance forecast. Selected callers are disjoint in the input attribution; no inclusive percentages are added.','inputs':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'projects':rows,'decision':'Do not implement a no-base-only map bypass as a presumed broad architectural win. First establish cost and eligibility of complete materialization, including inherited properties, recursive publication and table-demand frequency.'}
text=json.dumps(report,indent=2)+'\n'
import sys
if '--check' in sys.argv:assert (out/'report.json').read_text()==text
else:(out/'report.json').write_text(text)
print(json.dumps({r['project']:r['selectedMapPathPercent'] for r in rows}))
