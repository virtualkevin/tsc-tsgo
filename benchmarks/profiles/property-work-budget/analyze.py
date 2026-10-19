from pathlib import Path
import re,json,hashlib,subprocess
PATTERNS={
 'property_relation':r'checker\.\(\*Relater\)\.(?:propertiesRelatedTo|propertyRelatedTo|propertiesIdenticalTo)$',
 'property_lookup':r'checker\.\(\*Checker\)\.getPropert(?:yOfTypeEx|iesOfType|iesOfObjectType|iesOfUnionOrIntersectionType|yOfUnionOrIntersectionType)$',
 'member_materialization':r'checker\.\(\*Checker\)\.(?:instantiateSymbol|instantiateSymbols|resolveStructuredTypeMembers|getObjectTypeInstantiation)$',
 'mapper_execution':r'checker\.\(\*(?:TypeMapper|SimpleTypeMapper|ArrayTypeMapper|ArrayToSingleTypeMapper|DeferredTypeMapper|FunctionTypeMapper|MergedTypeMapper|CompositeTypeMapper|InferenceTypeMapper)\)\.Map$',
}
def analyze(raw):
 samples,locations=raw.split('Locations\n',1);locations=locations.split('Mappings\n')[0];lookup={};current=None
 for line in locations.splitlines():
  m=re.match(r'^\s*(\d+):\s+0x[0-9a-f]+(?:\s+M=\d+)?\s+(.*)',line)
  if m:current=int(m[1]);lookup[current]=[];line=m[2]
  else:line=line.strip()
  if current is None:continue
  f=re.match(r'(.+?)\s+\S+:\d+:\d+(?:\s+s=\d+(?:\(.*\))?)?$',line)
  if f:lookup[current].append(f[1])
 buckets={};total=0;inclusive=dict.fromkeys(PATTERNS,0)
 for line in samples.splitlines():
  m=re.match(r'^\s+\d+\s+(\d+):\s*(.*)$',line)
  if not m:continue
  cpu=int(m[1]);total+=cpu;frames=[]
  for i in map(int,m[2].split()):assert lookup[i];frames.extend(lookup[i])
  matched=tuple(k for k,p in PATTERNS.items() if any(re.search(p,f) for f in frames))
  key='+'.join(matched) or 'outside';buckets[key]=buckets.get(key,0)+cpu
  for k in matched:inclusive[k]+=cpu
 assert sum(buckets.values())==total and total>0
 prop=sum(v for k,v in buckets.items() if any(n in k.split('+') for n in ['property_relation','property_lookup','member_materialization']))
 return {'totalCpuNs':total,'inclusivePercent':{k:100*v/total for k,v in inclusive.items()},'exclusiveBucketsNs':buckets,'propertyUnionPercent':100*prop/total}
def main():
 root=Path(__file__).resolve().parents[3];p=Path(__file__).resolve().parent;inputs=json.loads((p.parent/'normal-map-attribution/inputs.json').read_text());rows=[]
 for entry in inputs:
  profile=Path(entry['profile']);assert hashlib.sha256(profile.read_bytes()).hexdigest()==entry['profileSha256']
  raw=subprocess.check_output(entry['command'],text=True);assert hashlib.sha256(raw.encode()).hexdigest()==entry['rawSha256']
  result=analyze(raw);rows.append({'project':entry['project'],'profileSha256':entry['profileSha256'],'rawSha256':entry['rawSha256'],**result})
  print(entry['project'],result['inclusivePercent'],'property union',result['propertyUnionPercent'])
 report={'scope':'Offline historical normal-build CPU samples, same retained production source. Inclusive categories overlap; exclusive buckets partition samples. Property union counts each matching sample once. Includes callees, not removable work, wall-time budget or speedup forecast. Sampling and workload variation apply.','patterns':PATTERNS,'projects':rows}
 (p/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
