from pathlib import Path
import re,json,collections,hashlib,tarfile,sys
PROJECT='github.com/microsoft/typescript-go/'
ARENA=PROJECT+'internal/core.(*Arena['
AST=PROJECT+'internal/ast.'
METRICS=['allocObjects','allocBytes','inuseObjects','inuseBytes']
def parse(raw):
 samples,locations=raw.split('Locations\n',1);locations=locations.split('Mappings\n')[0]
 assert 'alloc_objects/count alloc_space/bytes[dflt] inuse_objects/count inuse_space/bytes' in samples
 lookup={};current=None
 for line in locations.splitlines():
  m=re.match(r'^\s*(\d+):\s+0x[0-9a-f]+(?:\s+M=\d+)?\s+(.*)',line)
  if m:current=int(m[1]);lookup[current]=[];line=m[2]
  else:line=line.strip()
  if current is None:continue
  f=re.match(r'(.+?)\s+\S+:\d+:\d+(?:\s+s=\d+(?:\(.*\))?)?$',line)
  if f:lookup[current].append(f[1])
 for line in samples.splitlines():
  m=re.match(r'^\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+):\s*(.*)$',line)
  if not m:continue
  values=list(map(int,m.groups()[:4]));frames=[]
  for i in map(int,m[5].split()):
   assert lookup.get(i),('unparsed location',i)
   frames.extend(lookup[i])
  yield values,frames

def analyze(raw):
 totals=[0]*4;groups=collections.defaultdict(lambda:[0]*4);examples={}
 for values,frames in parse(raw):
  totals=[a+b for a,b in zip(totals,values)]
  positions=[i for i,f in enumerate(frames) if f.startswith(ARENA)]
  if not positions:continue
  # Innermost arena operation, then skip only contiguous arena wrappers.
  i=positions[0]+1
  while i<len(frames) and frames[i].startswith(ARENA):i+=1
  owner=next((f for f in frames[i:] if f.startswith(PROJECT)),'<no project owner>')
  groups[owner]=[a+b for a,b in zip(groups[owner],values)];examples.setdefault(owner,frames)
 def metrics(values):return dict(zip(METRICS,values))
 arena=[sum(v[i] for v in groups.values()) for i in range(4)]
 ast=[sum(v[i] for k,v in groups.items() if k.startswith(AST)) for i in range(4)]
 return {'total':metrics(totals),'arena':metrics(arena),'astOwnedArena':metrics(ast),'arenaPercent':{k:100*v/t if t else 0 for k,v,t in zip(METRICS,arena,totals)},'astOwnedArenaPercent':{k:100*v/t if t else 0 for k,v,t in zip(METRICS,ast,totals)},'owners':[{'name':k,**metrics(v),'exampleStack':examples[k]} for k,v in sorted(groups.items(),key=lambda kv:-kv[1][1])]}

def main():
 here=Path(__file__).resolve().parent;inputs=json.loads((here/'inputs.json').read_text())
 report={'scope':'Preserved sampled heap allocations, not timing, exact object counts, peak RSS, final-GC live heap, removable CPU or a speedup forecast. Each sample attributed once to its innermost Arena operation and nearest outer project caller after contiguous Arena wrappers. Inuse data reflects the profile collection state without forced final GC; recent allocation samples may be omitted. AST-owned arena is a subset of arena, not all AST storage.','projects':[]}
 with tarfile.open(here/'raw-heaps.tar.gz') as t:
  for item in inputs:
   data=t.extractfile(item['project']+'.raw.txt').read();assert hashlib.sha256(data).hexdigest()==item['rawSha256']
   r=analyze(data.decode());r.update(project=item['project'],rawSha256=item['rawSha256']);report['projects'].append(r)
 output=json.dumps(report,indent=2)+'\n'
 if '--write' in sys.argv:(here/'report.json').write_text(output)
 else:assert (here/'report.json').read_text()==output
 for p in report['projects']:
  print(p['project'],{k:round(v,3) for k,v in p['astOwnedArenaPercent'].items()})
  print([(x['name'],round(x['allocBytes']/1048576,2)) for x in p['owners'][:4]])
if __name__=='__main__':main()
