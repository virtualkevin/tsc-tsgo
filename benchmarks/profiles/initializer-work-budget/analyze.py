"""Rank semantic families using preserved CPU samples, without new compiler queries."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PARSER=HERE.parent/'property-work-budget/analyze.py'
PATTERNS={
 'initializer':r'checker\.\(\*Checker\)\.checkDeclarationInitializer$',
 'quick_expression':r'checker\.\(\*Checker\)\.getQuickTypeOfExpression$',
 'call_resolution':r'checker\.\(\*Checker\)\.(?:resolveCall|resolveCallExpression|resolveNewExpression|resolveTaggedTemplateExpression)$',
 'object_literal':r'checker\.\(\*Checker\)\.checkObjectLiteral$',
 'type_inference':r'checker\.\(\*Checker\)\.inferTypes$',
 'expression_cache':r'checker\.\(\*Checker\)\.checkExpressionCachedEx$',
 'instantiation':r'checker\.\(\*Checker\)\.instantiateTypeWithAlias$',
 'relation':r'checker\.\(\*Relater\)\.isRelatedToEx$',
}

sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
def main():
 spec=importlib.util.spec_from_file_location('profile_partition',PARSER)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 module.PATTERNS=PATTERNS
 inputs=HERE.parent/'normal-map-attribution/inputs.json'
 prior=json.loads((HERE.parent/'property-work-budget/report.json').read_text())
 prior={p['project']:p for p in prior['projects']}
 rows=[]
 for entry in json.loads(inputs.read_text()):
  assert sha(entry['profile'])==entry['profileSha256']
  raw=subprocess.check_output(entry['command'],text=True)
  assert hashlib.sha256(raw.encode()).hexdigest()==entry['rawSha256']
  result=module.analyze(raw);result.pop('propertyUnionPercent')
  assert result['totalCpuNs']==prior[entry['project']]['totalCpuNs']
  buckets=result['exclusiveBucketsNs'];total=result['totalCpuNs']
  initializer_cpu=sum(v for k,v in buckets.items() if 'initializer' in k.split('+'))
  result['initializerCpuPercent']=100*initializer_cpu/total
  result['initializerSubgroupsNs']={name:sum(v for k,v in buckets.items() if 'initializer' in k.split('+') and name in k.split('+')) for name in PATTERNS if name!='initializer'}
  row={'project':entry['project'],'profileSha256':entry['profileSha256'],'rawSha256':entry['rawSha256'],**result}
  rows.append(row)
  print(entry['project'],json.dumps(result['inclusivePercent']),'initializer CPU',result['initializerCpuPercent'])
 report={'scope':'Historical normal-build CPU samples from retained production. Inclusive categories overlap; exclusive buckets partition all samples and count recursive matches once. Costs include cache hits and callees, not duplicated or immutable work, removable time, or projected speedup. Initializer subgroups overlap and are not additive. No cross-checker equivalence conclusion.','patterns':PATTERNS,'inputsSha256':sha(inputs),'parserSha256':sha(PARSER),'projects':rows}
 (HERE/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
