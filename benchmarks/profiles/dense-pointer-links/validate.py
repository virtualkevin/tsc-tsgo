from pathlib import Path
import hashlib,json,os,subprocess
p=Path(__file__).resolve().parent
repo=p.parents[2]
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ('GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG'):env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
frozen={str(f.relative_to(p)):sha(f) for f in [*sorted((p/'staged').glob('*.go')),p/'overlay.json',Path(__file__)]}
results=[]
for name,flags in [('normal',[]),('race',['-race']),('checkptr',['-gcflags=all=-d=checkptr=2'])]:
 cmd=['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1','-overlay',str(p/'overlay.json'),*flags,'./internal/core','-run','^TestDensePointerLinks']
 with (p/(name+'.jsonl')).open('x') as out,(p/(name+'.stderr')).open('x') as err:
  code=subprocess.run(cmd,cwd=repo/'packages/tsc-go',env=env,stdout=out,stderr=err).returncode
 records=[json.loads(x) for x in (p/(name+'.jsonl')).read_text().splitlines()]
 passed=[x['Test'] for x in records if x.get('Action')=='pass' and 'Test' in x]
 assert code==0 and len(passed)==4 and not any(x.get('Action') in ('fail','skip') for x in records)
 results.append({'name':name,'command':cmd,'code':code,'passed':passed})
 assert all(sha(p/k)==v for k,v in frozen.items())
# A bounded mechanism microbenchmark, not a compiler workload or acceptance gate.
cmd=['/tmp/tsc-toolchains/go/bin/go','test','-count=5','-overlay',str(p/'overlay.json'),'./internal/core','-run','^$','-bench','^BenchmarkDensePointerLinksLookup$','-benchtime=200ms','-benchmem']
with (p/'lookup.stdout').open('x') as out,(p/'lookup.stderr').open('x') as err:
 code=subprocess.run(cmd,cwd=repo/'packages/tsc-go',env=env,stdout=out,stderr=err).returncode
assert code==0
assert all(sha(p/k)==v for k,v in frozen.items())
(p/'validation.json').write_text(json.dumps({'sources':frozen,'tests':results,'microbenchmark':{'command':cmd,'code':code}},indent=2)+'\n')
print('normal, race, checkptr and bounded lookup experiment passed',flush=True)
