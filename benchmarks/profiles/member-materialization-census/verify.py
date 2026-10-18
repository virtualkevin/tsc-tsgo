"""Read back completed diagnostic controls and their exact source/log inputs."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
r=read(out/'report.json');v=read(out/'validation.json');b=read(out/'build.json')
assert r['status']=='passed' and v['passed'] and b['exitCode']==0
assert sha(out/'capture.py')==r['controllerSha256'] and sha(out/'validation.json')==r['validationSha256']
assert sha(out/'validate.py')==v['controllerSha256'] and sha(out/'build.py')==b['controllerSha256']
assert {str(root/k):h for k,h in r['overlaySources'].items()}==v['overlaySources']==b['overlaySources']
for path,target in read(out/'overlay.json')['Replace'].items():assert sha(target)==v['overlaySources'][path]
assert len(v['runs'])==2
for run in v['runs']:
 assert run['passed'] and run['exitCode']==0
 path=out/(run['mode']+'.jsonl');assert sha(path)==run['stdoutSha256']
 assert sha(out/(run['mode']+'.stderr'))==run['stderrSha256']
 events=[json.loads(line) for line in path.read_text().splitlines()]
 assert not any(x['Action'] in ['fail','skip'] for x in events)
 assert len([x for x in events if x['Action']=='pass' and x.get('Test')])==3
assert len(r['runs'])==12
assert {(x['project'],x['mode']) for x in r['runs']}=={(p,m) for p in ['typeorm','trpc','vscode','sentry'] for m in ['baseline','disabled','enabled']}
rows=[]
for run in r['runs']:
 assert run['exitStatus']==0
 work=out/run['project']
 for stream in ['stdout','stderr']:
  path=work/(run['mode']+'.'+stream);assert path.read_bytes()==b'' and sha(path)==run[stream+'Sha256']
 group='small' if run['project'] in ['typeorm','trpc'] else 'large'
 ref=root/f'benchmarks/results/native-node-pointer/{group}.json';assert sha(ref)==run['referenceSha256']
 project=next(p for p in read(ref)['projects'] if p['name']==run['project'])
 assert run['cwd']==project['cwd'] and run['command'][1:]==project['args']
 for f in project['preflight']['candidate']['inputs']:assert sha(Path(project['cwd'])/f['file'])==f['sha256']
 assert len(project['preflight']['candidate']['inputs'])==run['inputCount']
 if run['mode']!='enabled':assert run['counts'] is None and run['censusSha256'] is None;continue
 assert sha(work/'census.json')==run['censusSha256']
 census=read(work/'census.json');counts=census['Counts'];assert counts==run['counts']
 assert census['Labels']==['start-no-bases','start-bases','start-resolving','retain-count-mismatch','retain-identity-mismatch','new-layout','reused-layout','table-immediate','table-later']
 assert census['Columns']==['events','entries','auxiliary']
 assert len(counts)==9 and all(len(x)==3 and all(type(n)==int and n>=0 for n in x) for x in counts)
 assert sum(counts[i][0] for i in [3,4,5,6])==counts[0][0]+counts[1][0]
 assert counts[7][0]+counts[8][0]<=counts[5][0]+counts[6][0]
 rows.append({'project':run['project'],'starts':sum(counts[i][0] for i in [0,1,2]),'recursiveStarts':counts[2][0],'newLayouts':counts[5][0],'reusedLayouts':counts[6][0],'immediateTableRequests':counts[7][0],'laterTableRequests':counts[8][0]})
assert sha(root/'packages/tsc-go/dist/tsc-go')==r['baselineSha256']
assert sha('/tmp/tsc-member-materialization-census')==r['candidateSha256']==b['binarySha256']
result={'passed':True,'reportSha256':sha(out/'report.json'),'controls':len(r['runs']),'projects':rows,'scope':'Diagnostic counts and artifact/input readback only; not timing or safe equivalence of materialization requests.'}
(out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
