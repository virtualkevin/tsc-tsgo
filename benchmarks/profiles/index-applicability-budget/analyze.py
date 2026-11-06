"""Partition preserved normal-build CPU samples; no compiler execution."""
from pathlib import Path
import hashlib, importlib.util, json, tarfile, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARSER = HERE.parent / 'property-work-budget/analyze.py'
PATTERNS = {
 'index_lookup': r'checker\.\(\*Checker\)\.findApplicableIndexInfo$',
 'index_predicate': r'checker\.\(\*Checker\)\.isApplicableIndexType$',
 'relation_entry': r'checker\.\(\*Checker\)\.isTypeRelatedTo$',
 'relation_check': r'checker\.\(\*Checker\)\.checkTypeRelatedTo$',
 'template_matching': r'checker\.\(\*Checker\)\.(?:isTypeMatchedByTemplateLiteralType|inferTypesFromTemplateLiteralType|inferFromLiteralPartsToTemplateLiteral)$',
 'relation_cache': r'checker\.\(\*Relation\)\.(?:get|set)$',
 'intersection_creation': r'checker\.\(\*Checker\)\.getIntersectionType$',
}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 spec = importlib.util.spec_from_file_location('cpu_partition', PARSER)
 parser = importlib.util.module_from_spec(spec); spec.loader.exec_module(parser)
 parser.PATTERNS = PATTERNS
 origin = HERE.parent / 'normal-map-attribution'
 inputs = json.loads((origin / 'inputs.json').read_text())
 capture = json.loads((HERE.parent / 'node-pointer-normal/manifest.json').read_text())
 projects = []
 with tarfile.open(origin / 'raw-profiles.tar.gz') as archive:
  for item in inputs:
   name = item['project']; raw = archive.extractfile(name + '.raw.txt').read()
   assert hashlib.sha256(raw).hexdigest() == item['rawSha256']
   assert capture['files'][name + '/' + Path(item['profile']).name] == item['profileSha256']
   row = parser.analyze(raw.decode()); row.pop('propertyUnionPercent')
   buckets = row['exclusiveBucketsNs']; total = row['totalCpuNs']
   def percent(predicate):
    return 100 * sum(v for k,v in buckets.items() if predicate(set(k.split('+')))) / total
   row['lookupOutsideRelationEntryPercent'] = percent(lambda names: 'index_lookup' in names and 'relation_entry' not in names)
   row['lookupWithFullRelationPercent'] = percent(lambda names: 'index_lookup' in names and 'relation_check' in names)
   row['lookupWithRelationCachePercent'] = percent(lambda names: 'index_lookup' in names and 'relation_cache' in names)
   row['lookupWithTemplateMatchingPercent'] = percent(lambda names: 'index_lookup' in names and 'template_matching' in names)
   row.update(project=name, rawSha256=item['rawSha256'], profileSha256=item['profileSha256'])
   projects.append(row)
   print(name, json.dumps({k:v for k,v in row.items() if k.endswith('Percent')}))
 source = {str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'packages/tsc-go/internal/checker/checker.go', ROOT/'packages/tsc-go/internal/checker/relater.go']}
 report = {'scope':'Historical normal-build CPU samples, not wall-time measurements. Inclusive categories overlap. Outside-relation samples include other callees, not just lookup-local instructions. No call counts, duplicate-query estimate, cache purity proof, or removable-runtime forecast.', 'patterns':PATTERNS, 'sources':source, 'parserSha256':sha(PARSER), 'inputsSha256':sha(origin/'inputs.json'), 'archiveSha256':sha(origin/'raw-profiles.tar.gz'), 'projects':projects}
 output = json.dumps(report, indent=2)+'\n'
 if '--verify' in sys.argv:
  assert (HERE/'report.json').read_text() == output
  print('Archived samples reproduce the report and current source hashes')
 else: (HERE/'report.json').write_text(output)
if __name__ == '__main__': main()
