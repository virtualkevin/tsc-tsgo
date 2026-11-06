"""Attribute mapped-member construction to source operations, counting each sample once."""
from pathlib import Path
import collections,hashlib,importlib.util,json,sys,tarfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2];PARSER=P.parent/'call-resolution-partition/analyze.py'
spec=importlib.util.spec_from_file_location('decoder',PARSER);decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
METHOD=decoder.PREFIX+'resolveMappedTypeMembers'
RULES=[
 ('publication','c.setStructuredTypeMembers('),
 ('preparation','typeParameter := c.getTypeParameterFromMappedType('),
 ('preparation','constraintType := c.getConstraintTypeFromMappedType('),
 ('preparation','nameType := c.getNameTypeFromMappedType('),
 ('preparation','shouldLinkPropDeclarations := c.getMappedTypeNameTypeKind('),
 ('preparation','templateType := c.getTemplateTypeFromMappedType('),
 ('preparation','modifiersType := c.getApparentType('),
 ('member_table','members := make('),
 ('member_table','existingProp := members['),
 ('member_table','members[propName] = prop'),
 ('link_tables','c.valueSymbolLinks.Get('),
 ('link_tables','c.mappedSymbolLinks.Get('),
 ('collision_unions','c.getUnionType('),
 ('modifier_property','modifiersProp = c.getPropertyOfType('),
 ('modifier_readonly','c.isReadonlySymbol('),
 ('symbol_creation','prop := c.newSymbol('),
 ('index_value_instantiation','propType := c.instantiateType('),
 ('modifier_index','modifiersIndexInfo := c.getApplicableIndexInfo('),
 ('index_creation','indexInfo := c.newIndexInfo('),
 ('index_merge','indexInfos = c.appendIndexInfo('),
 ('name_instantiation','propNameType = c.instantiateType('),
 ('enumeration','c.forEachMappedTypePropertyKeyTypeAndIndexSignatureKeyType('),
 ('lower_bound_enumeration','forEachType(c.getLowerBoundOfKeyType('),
]
def sites_from_source(source):
 inside=False;sites={};counts=collections.Counter()
 for number,line in enumerate(source.splitlines(),1):
  if line.startswith('func '):inside=line.startswith('func (c *Checker) resolveMappedTypeMembers(')
  if not inside:continue
  matches=[(stage,needle) for stage,needle in RULES if needle in line];assert len(matches)<=1,(number,line,matches)
  if matches:
   stage,needle=matches[0];sites[str(number)]=stage;counts[needle]+=1
 assert set(counts)=={needle for _,needle in RULES}
 assert all(n==(2 if needle in ['c.setStructuredTypeMembers(','c.valueSymbolLinks.Get(','c.mappedSymbolLinks.Get(','c.getUnionType('] else 1) for needle,n in counts.items()),counts
 return sites

def owns(name):return name==METHOD or name.startswith(METHOD+'.')
def partition(samples,sites):
 total=selected=0;stages=collections.Counter();lines=collections.Counter();flat=collections.defaultdict(collections.Counter);inclusive=collections.defaultdict(collections.Counter);owners=collections.Counter()
 for cpu,frames in samples:
  assert cpu>=0 and frames;total+=cpu
  owner=next((i for i,f in enumerate(frames) if owns(f[0])),None)
  if owner is None:continue
  selected+=cpu;name,_,line=frames[owner];stage=sites.get(str(line),'dispatch_or_unclassified');stages[stage]+=cpu;lines[str(line)]+=cpu;owners[name]+=cpu;flat[stage][frames[0][0]]+=cpu
  for f in {f[0] for f in frames[:owner]}:inclusive[stage][f]+=cpu
 assert sum(stages.values())==sum(lines.values())==sum(owners.values())==selected
 assert sum(sum(v.values()) for v in flat.values())==selected
 nested=lambda x:{k:dict(sorted(v.items())) for k,v in sorted(x.items())}
 return dict(totalCpuNs=total,selectedCpuNs=selected,selectedPercent=100*selected/total,stageNs=dict(sorted(stages.items())),stagePercentTotal={k:100*v/total for k,v in sorted(stages.items())},sourceLineNs=dict(sorted(lines.items())),ownerFramesNs=dict(sorted(owners.items())),flatFunctionsByStage=nested(flat),inclusiveFunctionsByStage=nested(inclusive))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 prior=json.loads((P.parent/'call-resolution-partition/report.json').read_text());source=ROOT/'packages/tsc-go/internal/checker/checker.go';assert sha(source)==prior['sourceSha256'] and sha(PARSER)==prior['analyzerSha256'];sites=sites_from_source(source.read_text());base=P.parent/'normal-map-attribution';assert sha(base/'raw-profiles.tar.gz')==prior['archiveSha256'] and sha(base/'inputs.json')==prior['inputsSha256'];inputs=json.loads((base/'inputs.json').read_text());rows=[]
 with tarfile.open(base/'raw-profiles.tar.gz') as tar:
  for item,old in zip(inputs,prior['projects'],strict=True):
   assert item['project']==old['project'];raw=tar.extractfile(item['project']+'.raw.txt').read();assert hashlib.sha256(raw).hexdigest()==item['rawSha256']==old['rawSha256'];row=partition(decoder.decode(raw.decode()),sites);assert row['totalCpuNs']==old['totalCpuNs'];rows.append(dict(project=item['project'],rawSha256=item['rawSha256'],**row))
 report=dict(scope='Historical normal CPU; each sample belongs to its innermost mapped-construction method or closure frame. Source callsite stages and flat rows partition selected samples; inclusive descendant rows overlap. Not wall time, allocation counts, duplicate work, purity or a speedup forecast. Unknown source lines remain explicit. No compiler execution.',sourceSha256=sha(source),parserSha256=sha(PARSER),priorSha256=sha(P.parent/'call-resolution-partition/report.json'),archiveSha256=sha(base/'raw-profiles.tar.gz'),inputsSha256=sha(base/'inputs.json'),analyzerSha256=sha(__file__),sites=sites,projects=rows)
 encoded=json.dumps(report,indent=2)+'\n'
 if '--write' in sys.argv:(P/'report.json').write_text(encoded)
 else:assert encoded==(P/'report.json').read_text()
 for row in rows:print(row['project'],row['selectedPercent'],json.dumps(row['stagePercentTotal']))
if __name__=='__main__':main()
