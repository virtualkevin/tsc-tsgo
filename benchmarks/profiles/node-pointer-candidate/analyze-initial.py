from pathlib import Path
import re,json,collections,hashlib
D=Path('/tmp/tsc-census-families');out=Path('/tmp/tsc-map-callers');report={'scope':'Disjoint assignment of samples containing builtin-map frames to nearest project caller; inclusive map path CPU, not isolated lookup latency or removable work','projects':[]}
for project in ['trpc','typeorm','vscode','sentry']:
 p=D/project/'4-base-profiles/cpu.raw.txt';text=p.read_text();samples,locations=text.split('Locations\n',1);locations=locations.split('Mappings\n')[0]
 lookup={};current=None
 for line in locations.splitlines():
  m=re.match(r'^\s*(\d+):\s+0x[0-9a-f]+(?:\s+M=\d+)?\s+(.*)',line)
  if m:current=int(m[1]);lookup[current]=[];line=m[2]
  else:line=line.strip()
  if current is None:continue
  f=re.match(r'(.+?)\s+\S+:\d+:\d+(?:\s+s=\d+)?$',line)
  if f:lookup[current].append(f[1])
 totals=collections.Counter();allcpu=0;mapcpu=0;unmapped=set();examples={}
 for line in samples.splitlines():
  m=re.match(r'^\s+\d+\s+(\d+):\s*(.*)$',line)
  if not m:continue
  cpu=int(m[1]);allcpu+=cpu;ids=[int(x) for x in m[2].split()];frames=[]
  for i in ids:
   assert i in lookup,i
   if not lookup[i]:unmapped.add(i)
   frames.extend(lookup[i])
  indices=[i for i,f in enumerate(frames) if f.startswith('internal/runtime/maps.') or re.match(r'runtime\.map(access|assign|delete|iter|clear)',f)]
  if not indices:continue
  mapcpu+=cpu
  caller=next((f for f in frames[indices[0]+1:] if f.startswith('github.com/microsoft/typescript-go/')),'<no project caller>')
  totals[caller]+=cpu;examples.setdefault(caller,frames)
 assert sum(totals.values())==mapcpu
 row={'project':project,'rawSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'totalCpuNs':allcpu,'mapPathCpuNs':mapcpu,'mapPathPercent':mapcpu/allcpu*100,'unparsedLocationIds':sorted(unmapped),'callers':[{'name':n,'cpuNs':v,'totalPercent':v/allcpu*100,'exampleStack':examples[n]} for n,v in totals.most_common()]};report['projects'].append(row)
 print(project,round(row['mapPathPercent'],2),'unparsed',len(unmapped))
 for n,v in totals.most_common(10):print(round(v/allcpu*100,2),n)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
