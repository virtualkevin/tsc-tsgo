from pathlib import Path
import re,json,collections,hashlib,sys
def analyze(text):
 samples,locations=text.split('Locations\n',1);locations=locations.split('Mappings\n')[0]
 lookup={};current=None
 for line in locations.splitlines():
  m=re.match(r'^\s*(\d+):\s+0x[0-9a-f]+(?:\s+M=\d+)?\s+(.*)',line)
  if m:current=int(m[1]);lookup[current]=[];line=m[2]
  else:line=line.strip()
  if current is None:continue
  f=re.match(r'(.+?)\s+\S+:\d+:\d+(?:\s+s=\d+(?:\(.*\))?)?$',line)
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
  indices=[i for i,f in enumerate(frames) if re.match(r'^runtime\.map(?:access|assign|delete).*_faststr$',f)]
  if not indices:continue
  mapcpu+=cpu
  caller=next((f for f in frames[indices[0]+1:] if f.startswith('github.com/microsoft/typescript-go/')),'<no project caller>')
  totals[caller]+=cpu;examples.setdefault(caller,frames)
 assert sum(totals.values())==mapcpu
 assert allcpu>0 and not unmapped, sorted(unmapped)
 return {'totalCpuNs':allcpu,'fastStringMapPathCpuNs':mapcpu,'fastStringMapPathPercent':mapcpu/allcpu*100,'unparsedLocationIds':sorted(unmapped),'callers':[{'name':n,'cpuNs':v,'totalPercent':v/allcpu*100,'exampleStack':examples[n]} for n,v in totals.most_common()]}

def main():
 d=Path(sys.argv[1]); report={'scope':'Offline retained-profile audit of samples containing a specialized runtime string-key map access/assignment/deletion entry point. Each matching sample is attributed once to its nearest project caller above the innermost matching entry point. Includes allocation/hash callees. Generic entry points and iterator-only samples are excluded even if their keys might be strings. Not isolated hashing cost, lookup counts, removable work, wall time or a speedup forecast.','projects':[]}
 for project in ['trpc','typeorm','vscode','sentry']:
  p=d/(project+'.raw.txt');r=analyze(p.read_text());r.update(project=project,rawSha256=hashlib.sha256(p.read_bytes()).hexdigest());report['projects'].append(r)
  print(project,round(r['fastStringMapPathPercent'],3))
  for x in r['callers'][:8]: print(round(x['totalPercent'],3),x['name'])
 Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
