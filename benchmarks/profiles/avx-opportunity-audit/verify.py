from pathlib import Path
import gzip,hashlib,importlib.util,json,re
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
r=json.loads((p/'report.json').read_text());assert sha(p/'capture.py')==r['controllerSha256']
parser=p.parent/'property-work-budget/analyze.py';assert sha(parser)==r['parserSha256']
spec=importlib.util.spec_from_file_location('budget',parser);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.PATTERNS=r['patterns']
for x in r['projects']:
 raw=gzip.decompress((p/(x['workload']+'.raw.gz')).read_bytes())
 assert sha(p/(x['workload']+'.raw.gz'))==x['archiveSha256'] and hashlib.sha256(raw).hexdigest()==x['rawSha256']
 result=m.analyze(raw.decode());result.pop('propertyUnionPercent')
 assert all(result[k]==x[k] for k in result)
for x in r['assembly']:
 file=p/(x['symbol']+'.asm');assert sha(file)==x['sha256']
 text=file.read_text();assert '<'+x['symbol']+'>:' in text
 lines=[line for line in text.splitlines() if re.search(r'\b(?:v[a-z0-9]+|pcmpeqb|pmovmskb)\s',line)]
 assert lines==x['vectorInstructionLines'] and any('%ymm' in line for line in lines)
(p/'readback.json').write_text(json.dumps({'passed':True,'reportSha256':sha(p/'report.json'),'verifierSha256':sha(__file__),'scope':'Raw profile hash and budget reproduction; assembly hashes and vector-line reproduction, YMM path present in every inspected routine. Not dynamic SIMD execution proof.'},indent=2)+'\n')
print('Verified all four profile budgets and shipped vector paths')
