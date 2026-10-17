from pathlib import Path
import collections,hashlib,json,re,sys

def flags(r):
 return r['ReturnedNormally']!=r['Calls'] or any(r[x] for x in ['ErrorResults','DeferredResults','DiagnosticSpans'])

def repeats(r):
 n=r['Calls']-1-r['NestedSameRawKeyEntries']
 assert r['Calls']>0 and n>=0
 return n

def category(r):
 if r['Calls']==1:return 'single-entry-record'
 if not repeats(r):return 'nested-only-repeat-record'
 return 'nonnested-repeat-record-'+('flagged' if flags(r) else 'unflagged')

def parse_samples(raw):
 samples=[]
 for line in raw.split('Samples:\n',1)[1].split('Locations\n',1)[0].splitlines():
  m=re.match(r'^\s+(\d+)\s+(\d+):',line)
  if m:samples.append({'cpu':int(m[2]),'labels':{}})
  elif 'census_' in line:
   assert samples
   labels=dict(re.findall(r'(census_\w+):\[([^\]]+)\]',line))
   assert set(labels)=={'census_checker','census_family','census_record'}
   assert not samples[-1]['labels'];samples[-1]['labels']=labels
 assert samples
 return samples

def analyze(rows,samples):
 owners={str(x['checkerId']):x for x in rows};assert len(owners)==len(rows)
 records={};families=collections.defaultdict(collections.Counter);overflow=0
 for owner,o in owners.items():
  assert o['cpuLabels'];overflow+=o['overflow']['Calls']
  for index,r in enumerate(o['records']):
   assert r['ID']==index
   key=(owner,str(index));records[key]=r;f=families[r['Family']]
   f['records']+=1;f['calls']+=r['Calls'];f['nestedEntries']+=r['NestedSameRawKeyEntries'];f['nonnestedReentries']+=repeats(r)
   if repeats(r):
    f['recordsWithNonnestedReentries']+=1
    if not flags(r):f['unflaggedNonnestedReentries']+=repeats(r)
 buckets=collections.Counter();cpu=collections.Counter()
 for s in samples:
  l=s['labels']
  if not l:buckets['unlabeled']+=s['cpu'];continue
  owner=owners[l['census_checker']]
  if l['census_record']=='overflow':
   assert owner['overflow']['Family']==l['census_family'];buckets['overflow']+=s['cpu'];continue
  key=(l['census_checker'],l['census_record']);r=records[key];assert r['Family']==l['census_family']
  buckets[category(r)]+=s['cpu'];cpu[key]+=s['cpu']
 total=sum(s['cpu'] for s in samples);assert total==sum(buckets.values()) and total>0
 ranked=[]
 for key,r in records.items():
  if not repeats(r):continue
  ranked.append({'checkerId':key[0],'recordId':int(key[1]),'family':r['Family'],'calls':r['Calls'],'nonnestedReentries':repeats(r),'flagged':flags(r),'allEntriesSampledCpuNs':cpu[key],'file':r['File'],'pos':r['Pos'],'mode':r['Mode'],'candidates':r['Candidates'],'resolving':r['Resolving'],'aliasPresent':r['AliasAddress']!='0x0','flowDepth':r['FlowDepth'],'instantiationDepth':r['InstantiationDepth']})
 ranked.sort(key=lambda r:(-r['allEntriesSampledCpuNs'],-r['nonnestedReentries'],r['checkerId'],r['recordId']))
 return {'totalCpuNs':total,'sampledCpuBucketsNs':dict(buckets),'sampledCpuBucketFractions':{k:v/total for k,v in buckets.items()},'families':dict(families),'overflowCalls':overflow,'recordedCalls':sum(r['Calls'] for r in records.values()),'topRepeatedRecordsByAllEntriesCpu':ranked[:30]}

def main():
 directory=Path(sys.argv[1]);result={'scope':'Offline audit of historical insertion-order-capped detailed tRPC census. Raw-key matches are not context-complete equivalence. CPU assigned to repeated records includes first and subsequent calls and inherited labels; it is not repeated-call CPU or removable work. Unflagged means only the recorded flags are absent. Overflow remains unclassified. No new compiler run or production change.','runs':[]}
 for name in ['1-labeled','4-labeled']:
  census=directory/(name+'.census.jsonl');profile=directory/(name+'.cpu.raw.txt');rows=[json.loads(x) for x in census.read_text().splitlines()]
  assert rows[0]['semanticallyEquivalentResultsProven'] is False
  r=analyze(rows[1:],parse_samples(profile.read_text()));r.update(name=name,censusSha256=hashlib.sha256(census.read_bytes()).hexdigest(),rawCpuSha256=hashlib.sha256(profile.read_bytes()).hexdigest());result['runs'].append(r)
 Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps([{'name':r['name'],'cpuFractions':r['sampledCpuBucketFractions'],'families':r['families'],'overflowCalls':r['overflowCalls'],'recordedCalls':r['recordedCalls']} for r in result['runs']],indent=2))
if __name__=='__main__':main()
