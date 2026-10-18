from pathlib import Path
import json,collections,hashlib
from heap_parser import parse,METRICS,PROJECT

def classify(records):
 total=[0]*4;groups=collections.defaultdict(lambda:[0]*4)
 for values,frames in records:
  assert len(values)==4 and all(v>=0 for v in values)
  # Assign each sample once. Skip generic allocation/storage wrappers to expose
  # their project consumer, without summing overlapping inclusive stacks.
  owner=next((f for f in frames if f.startswith(PROJECT) and not f.startswith((PROJECT+'internal/core.',PROJECT+'internal/collections.'))),'<runtime or generic-only>')
  total=[a+b for a,b in zip(total,values)];groups[owner]=[a+b for a,b in zip(groups[owner],values)]
 assert total==[sum(v[i] for v in groups.values()) for i in range(4)]
 return {'total':dict(zip(METRICS,total)),'owners':[{'name':k,**dict(zip(METRICS,v))} for k,v in sorted(groups.items(),key=lambda kv:(-kv[1][3],kv[0]))]}

def main():
 p=Path(__file__).resolve().parent;d=json.loads((p/'decoded.json').read_text());assert d['status']=='passed';report={'scope':'Sampled heap after completed CLI work with Program retained. Each sample assigned once to its first non-core/non-collections project frame. Not exact object counts, a peak, semantic necessity, removable bytes or timing. Profiling/GC perturbs execution and profiles include observer allocations. Before/after may differ due to sample publication, reclamation and observer overhead.','projects':[]}
 for name in ['typeorm','trpc','vscode','sentry']:
  result={'project':name}
  for phase in ['before','after']:
   f=p/name/'heap'/(phase+'.raw.txt');record=next(x for x in d['profiles'] if x['project']==name and x['phase']==phase)
   assert hashlib.sha256(f.read_bytes()).hexdigest()==record['rawSha256']
   result[phase]=classify(parse(f.read_text()))
  result['memStats']=json.loads((p/name/'heap/stats.json').read_text());report['projects'].append(result)
 output=json.dumps(report,indent=2)+'\n'
 import sys
 if '--write' in sys.argv:(p/'analysis.json').write_text(output)
 else:assert (p/'analysis.json').read_text()==output
 for x in report['projects']:print(x['project'],x['after']['total'],[(y['name'].split('/')[-1],round(y['inuseBytes']/1048576,1)) for y in x['after']['owners'][:8]])
if __name__=='__main__':main()
