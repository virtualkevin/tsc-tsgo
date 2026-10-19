from pathlib import Path
import json
from counts import validate
p=Path(__file__).resolve().parent
report=json.loads((p/'report.json').read_text());assert report['status']=='passed'
wrappers={'(*pendingInstantiatedMembers).materialize','(*pendingInstantiatedMembers).materializeTable','(*StructuredType).Properties','(*StructuredType).Members','(*Checker).getPropertiesOfType','(*Checker).getPropertiesOfObjectType'}
rows=[]
for project in ['typeorm','trpc','vscode','sentry']:
 data=json.loads((p/project/'census.json').read_text());v=validate(data);c=v['categories'];stacks={};callers={}
 for owner in data['Owners']:
  for stack,values in (owner['Stacks'] or {}).items():
   sums=stacks.setdefault(stack,[0,0]);sums[0]+=values[0];sums[1]+=values[1]
   functions=[line.rsplit(':',1)[0].removeprefix('github.com/microsoft/typescript-go/internal/checker.') for line in stack.splitlines() if line!='possibly truncated']
   caller=next((f for f in functions if f not in wrappers),'truncated-or-wrapper-only')
   sums=callers.setdefault(caller,[0,0]);sums[0]+=values[0];sums[1]+=values[1]
 row={'project':project,'lookups':c['lookup'],'boundaries':{k:{'count':n,'fractionOfLookups':n/c['lookup']} for k,n in c.items() if k.startswith('lookup-')},'bulkMaterializations':c['bulk-materializations'],'bulkSourceSlots':c['bulk-source-slots'],'sampledEvents':sum(x[0] for x in stacks.values()),'sampledCallers':[{'caller':k,'sampledEvents':v[0],'sampledSourceSlots':v[1]} for k,v in sorted(callers.items(),key=lambda x:(-x[1][0],x[0]))],'topStacks':[{'stack':k,'sampledEvents':v[0],'sampledSourceSlots':v[1]} for k,v in sorted(stacks.items(),key=lambda x:(-x[1][0],x[0]))[:12]]}
 assert sum(x['count'] for x in row['boundaries'].values())==row['lookups']
 assert sum(x['sampledEvents'] for x in row['sampledCallers'])==row['sampledEvents']
 rows.append(row)
 print(json.dumps({'project':project,'largestBoundaries':sorted(row['boundaries'].items(),key=lambda x:-x[1]['count'])[:4],'bulkMaterializations':row['bulkMaterializations'],'topSampledCallers':row['sampledCallers'][:5]}))
(p/'summary.json').write_text(json.dumps({'scope':'Ordered diagnostic exclusions and systematically sampled materialization callers. Not CPU cost, liveness, random estimation or speedup evidence.','omittedDispatchWrappers':sorted(wrappers),'results':rows},indent=2)+'\n')
