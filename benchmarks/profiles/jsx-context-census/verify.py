from pathlib import Path
import hashlib,json,re,subprocess,sys
sys.dont_write_bytecode=True
from counts import validate
p=Path(__file__).resolve().parent;root=p.parents[2]
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
sources={k:sha(v) for k,v in json.loads((p/'overlay.json').read_text())['Replace'].items()}
v=json.loads((p/'validation.json').read_text());assert v['status']=='passed' and v['sources']==sources
assert [r['name'] for r in v['results']]==['normal','race','checkptr']
for run in v['results']:
 flags={'normal':[],'race':['-race'],'checkptr':['-gcflags=all=-d=checkptr=2']}[run['name']]
 assert run['command']==['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1','-overlay',str(p/'overlay.json'),*flags,'./internal/checker','-run','^TestJsxContext']
 events=[json.loads(x) for x in (p/(run['name']+'.stdout')).read_text().splitlines()]
 names=[e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e]
 assert run['exitCode']==0 and set(names)==set(run['passed'])=={'TestJsxContextNestedCompletion','TestJsxContextKeyAndCap','TestJsxContextEffectsAndExclusiveOutput','TestJsxContextActualCheckerDifferential'}
 assert not any(e.get('Action') in ['skip','fail','build-fail'] for e in events)
subprocess.run([sys.executable,str(p/'audit_source.py')],check=True)
build=json.loads((p/'build.json').read_text());assert build['exitCode']==0 and build['overlaySources']==sources
assert build['controllerSha256']==sha(p/'build.py') and build['buildInfoSha256']==sha(p/'build-info.txt')
report=json.loads((p/'report.json').read_text());assert report['status']=='passed' and report['overlaySources']==sources
for field,name in [('controllerSha256','capture.py'),('countsValidatorSha256','counts.py'),('validationSha256','validation.json'),('buildReportSha256','build.json')]:assert report[field]==sha(p/name)
assert len(report['runs'])==12
expected={(name,4,mode) for name in ['typeorm','trpc','vscode','sentry'] for mode in ['baseline','disabled','enabled']}
assert {(r['project'],r['checkers'],r['mode']) for r in report['runs']}==expected
flagsSource=root/'packages/tsc-go/internal/checker/types.go'
flags={1<<int(bit):name.removeprefix('TypeFlags') for name,bit in re.findall(r'(TypeFlags\w+)\s+TypeFlags\s*=\s*1\s*<<\s*(\d+)',flagsSource.read_text())}
def names(value):
 assert value & ~sum(flags)==0
 return [name for bit,name in flags.items() if value&bit]
summaries=[]
for run in report['runs']:
 assert run['exitStatus']==0 and run['elapsedNs']>0
 ref=root/run['reference'];assert sha(ref)==run['referenceSha256']
 project=next(x for x in json.loads(ref.read_text())['projects'] if x['name']==run['project'])
 assert run['inputCount']==len(project['preflight']['candidate']['inputs']) and run['cwd']==project['cwd']
 assert run['command'][1:]==[*project['args'],'--checkers','4']
 directory=p/run['project']
 for stream in ['stdout','stderr']:
  f=directory/('4-'+run['mode']+'.'+stream)
  assert f.read_bytes()==b'' and sha(f)==run[stream+'Sha256']
 for name,item in run['artifacts'].items():
  f=directory/name;assert sha(f)==item['sha256'] and f.stat().st_size==item['bytes']
 if run['mode']=='enabled':
  raw=json.loads((directory/'4-census.json').read_text());assert len(raw['Owners'])==4;totals=validate(raw);assert totals==run['counts']
  summaries.append({'project':run['project'],'owners':len(raw['Owners']),'saturatedOwners':sum(o['TrackedRequests']==o['RequestLimit'] for o in raw['Owners']),'totals':totals})
summary={'scope':'Diagnostic counts only. Bounded early-request history is biased; inference pointer identity is not immutable state and repeated keys or unchanged result TypeIDs do not prove cache equivalence. No speedup or removable CPU claim.','flagsSourceSha256':sha(flagsSource),'projects':summaries}
(p/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(p/'readback.json').write_text(json.dumps({'passed':True,'sources':sources,'files':{n:sha(p/n) for n in ['validation.json','build.json','report.json','summary.json','source-audit.json','normal.stdout','normal.stderr','race.stdout','race.stderr','checkptr.stdout','checkptr.stderr']},'verifierSha256':sha(__file__)},indent=2)+'\n')
for s in summaries:print(s['project'],s['saturatedOwners'],s['totals'])
print('All 12 controls and focused raw logs verified')
