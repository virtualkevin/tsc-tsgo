from pathlib import Path
import subprocess,json,hashlib,os,collections,signal
root=Path('/home/dev/tssss/tsc-tsgo');pilot=Path('/tmp/tsc-indexed-symbol-pilot');out=pilot/'focused-validation';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected={'TestSymbolAllocationHandlesPreserveLazySemanticIDs','TestSymbolAllocationHandleExhaustionDoesNotWrap','TestSymbolAllocationHandleConcurrentOwners','TestIndexedPointerLinksBoundariesIdentityAndReplacement','TestIndexedPointerLinksReadonlyMissesAndReaders','TestIndexedPointerLinksTypedRootsAndDisplacedValues'}
overlay=pilot/'combined-overlay.json';replacements=json.load(open(overlay))['Replace'];frozen={p:sha(p) for p in replacements.values()};frozen[str(overlay)]=sha(overlay)
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','GOOS','GOARCH','GOAMD64','GOCOVERDIR']:env.pop(k,None)
env['GOCACHE']='/home/dev/.cache/go-build';env['GOTOOLCHAIN']='local'
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
def capture():return json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,env=env,text=True))
before=capture();assert before['sha256']=='78b76607d79c501f3c35fcbbec5a880561699244c7d65daab6f27f42b22f9337'
report={'scope':'Focused isolated Go-overlay tests only; no production compiler build or workload performance claim','sourceSha256':before['sha256'],'head':before['revision'],'overlayFiles':frozen,'runs':[],'passed':False}
try:
 for name,flags in [('normal',[]),('race',['-race']),('checkptr',['-gcflags=all=-d=checkptr=2'])]:
  command=['/tmp/tsc-toolchains/go/bin/go','test','-overlay',str(overlay),'-json',*flags,'./internal/core','./internal/ast','-run','^Test(SymbolAllocation|IndexedPointerLinks)','-count=1','-timeout','10m']
  with (out/(name+'.jsonl')).open('w') as stdout,(out/(name+'.stderr')).open('w') as stderr:
   child=subprocess.Popen(command,cwd=root/'packages/tsc-go',env=env,stdout=stdout,stderr=stderr,start_new_session=True)
   try:code=child.wait(timeout=660)
   except BaseException:
    os.killpg(child.pid,signal.SIGKILL);child.wait();raise
  events=[json.loads(l) for l in (out/(name+'.jsonl')).read_text().splitlines() if l.startswith('{')]
  terminal=[e for e in events if e['Action'] in ['pass','fail','skip']]
  tests=[e for e in terminal if e.get('Test')];packages=[e for e in terminal if not e.get('Test')]
  ok=code==0 and {e['Test'] for e in tests}==expected and len(tests)==6 and all(e['Action']=='pass' for e in tests+packages) and len(packages)==2
  record={'name':name,'command':command,'exitCode':code,'passed':ok,'testRecords':dict(collections.Counter(e['Action'] for e in tests)),'packages':{e['Package']:e['Action'] for e in packages},'stdoutSha256':sha(out/(name+'.jsonl')),'stderrSha256':sha(out/(name+'.stderr'))};report['runs'].append(record);print(name,code,ok,flush=True)
  assert ok,'focused test gate failed'
  assert all(sha(p)==v for p,v in frozen.items()),'overlay source changed'
 after=capture();report['mainSourceUnchanged']=before['sha256']==after['sha256'] and before['revision']==after['revision'];report['passed']=report['mainSourceUnchanged'] and len(report['runs'])==3
except BaseException as e:report['error']=str(e)
finally:(out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
print('terminal passed='+str(report['passed']),flush=True)
raise SystemExit(0 if report['passed'] else 1)
