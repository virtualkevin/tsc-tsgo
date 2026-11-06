from pathlib import Path
import hashlib,importlib.util,json,sys,tarfile
P=Path(__file__).resolve().parent;BASE=P.parent/'normal-map-attribution';PARSER=P.parent/'property-work-budget/analyze.py'
spec=importlib.util.spec_from_file_location('cpu_parser',PARSER);parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
parser.PATTERNS={'mark_or_assist':r'runtime\.(?:gcBgMarkWorker(?:\.|$)|gcAssistAlloc(?:\.|$))'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=json.loads((P.parent/'call-resolution-partition/report.json').read_text());assert sha(BASE/'raw-profiles.tar.gz')==prior['archiveSha256'];assert sha(BASE/'inputs.json')==prior['inputsSha256']
rows=[]
with tarfile.open(BASE/'raw-profiles.tar.gz') as tar:
 for item,old in zip(json.loads((BASE/'inputs.json').read_text()),prior['projects'],strict=True):
  assert item['project']==old['project'];raw=tar.extractfile(item['project']+'.raw.txt').read();assert hashlib.sha256(raw).hexdigest()==item['rawSha256']==old['rawSha256'];r=parser.analyze(raw.decode());r.pop('propertyUnionPercent');assert r['totalCpuNs']==old['totalCpuNs'];rows.append(dict(project=item['project'],rawSha256=item['rawSha256'],**r))
report=dict(scope='Historical CPU samples containing background GC mark-worker or mutator-assist frames, counted once. Not all GC work, wall time, removable work, or predicted classic-GC savings.',patterns=parser.PATTERNS,parserSha256=sha(PARSER),archiveSha256=sha(BASE/'raw-profiles.tar.gz'),inputsSha256=sha(BASE/'inputs.json'),analyzerSha256=sha(__file__),projects=rows)
text=json.dumps(report,indent=2)+'\n'
if '--write' in sys.argv:(P/'budget.json').write_text(text)
else:assert (P/'budget.json').read_text()==text
for r in rows:print(r['project'],r['inclusivePercent'])
