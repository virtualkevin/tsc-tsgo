from pathlib import Path
import re,json,collections,hashlib,tarfile,sys
PREFIX='github.com/microsoft/typescript-go/internal/checker.'
MEMBER=PREFIX+'getResolvedMember'
WRAPPERS={PREFIX+'(*Checker).'+n for n in ['getPropertyOfObjectType','getPropertyOfTypeEx','getPropertyOfType']}
OPERATIONS={name:PREFIX+method for name,method in [('propertiesRelatedTo','(*Relater).propertiesRelatedTo'),('createUnionOrIntersectionProperty','(*Checker).createUnionOrIntersectionProperty'),('inferFromProperties','(*Checker).inferFromProperties')]}
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
 totals={kind:collections.Counter() for kind in ['memberPath','memberDirectStringMap']}
 examples={kind:{} for kind in totals};allcpu=0;unmapped=set();operations=collections.Counter()
 for line in samples.splitlines():
  m=re.match(r'^\s+\d+\s+(\d+):\s*(.*)$',line)
  if not m:continue
  cpu=int(m[1]);allcpu+=cpu;frames=[]
  for i in map(int,m[2].split()):
   assert i in lookup,i
   if not lookup[i]:unmapped.add(i)
   frames.extend(lookup[i])
  for name,frame in OPERATIONS.items():
   if frame in frames:operations[name]+=cpu
  if MEMBER not in frames:continue
  index=frames.index(MEMBER)
  above=[f for f in frames[index+1:] if f.startswith('github.com/microsoft/typescript-go/') and f not in WRAPPERS]
  caller=above[0] if above else '<no project caller>'
  totals['memberPath'][caller]+=cpu;examples['memberPath'].setdefault(caller,frames)
  maps=[i for i,f in enumerate(frames) if re.match(r'^runtime\.map(?:access|assign|delete).*_faststr$',f)]
  if maps:
   nearest=next((f for f in frames[maps[0]+1:] if f.startswith('github.com/microsoft/typescript-go/')),None)
   if nearest==MEMBER:
    totals['memberDirectStringMap'][caller]+=cpu;examples['memberDirectStringMap'].setdefault(caller,frames)
 assert allcpu>0 and not unmapped,sorted(unmapped)
 result={'totalCpuNs':allcpu,'inclusiveOperations':{name:{'cpuNs':operations[name],'totalPercent':100*operations[name]/allcpu} for name in OPERATIONS}}
 for kind,counts in totals.items():
  total=sum(counts.values())
  result[kind]={'cpuNs':total,'totalPercent':100*total/allcpu,'callers':[{'name':n,'cpuNs':v,'totalPercent':100*v/allcpu,'memberCategoryPercent':100*v/total,'exampleStack':examples[kind][n]} for n,v in counts.most_common()]}
 return result

def main():
 here=Path(__file__).resolve().parent;prior=here.parent/'normal-map-attribution'
 inputs=json.loads((prior/'inputs.json').read_text())
 report={'scope':'Retained CPU profiles, each sample counted once per overlapping category. memberPath includes all callees of innermost getResolvedMember; memberDirectStringMap restricts to specialized string-map runtime paths whose nearest project caller is getResolvedMember. Attribution skips only three named property lookup wrappers. No hit/miss distinction, request counts, causality, removable CPU budget or wall-time forecast. Categories overlap and must not be added.','skippedWrappers':sorted(WRAPPERS),'projects':[]}
 with tarfile.open(prior/'raw-profiles.tar.gz') as archive:
  for item in inputs:
   data=archive.extractfile(item['project']+'.raw.txt').read();assert hashlib.sha256(data).hexdigest()==item['rawSha256']
   result=analyze(data.decode());result.update(project=item['project'],rawSha256=item['rawSha256']);report['projects'].append(result)
 text=json.dumps(report,indent=2)+'\n'
 if '--write' in sys.argv:(here/'report.json').write_text(text)
 else:assert (here/'report.json').read_text()==text
 for r in report['projects']:
  print(r['project'])
  for kind in ['memberPath','memberDirectStringMap']:
   print(kind,round(r[kind]['totalPercent'],3))
   for c in r[kind]['callers'][:8]:print(round(c['totalPercent'],3),c['name'])
if __name__=='__main__':main()
