from pathlib import Path
import os,json,hashlib,subprocess
root=Path(__file__).resolve().parents[3]; out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
def source():return json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,text=True))
before=source(); assert before['sha256']=='216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd'
baseline=root/'packages/tsc-go/dist/tsc-go';candidate=Path('/tmp/tsc-argument-request-census')
assert sha(baseline)=='8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f'
tests=[json.loads(l) for l in (out/'tests.jsonl').read_text().splitlines()];assert any(e.get('Test')=='TestArgumentRequestCensus' and e['Action']=='pass' for e in tests);assert not any(e['Action'] in ['fail','skip'] for e in tests)
overlay=json.loads((out/'overlay.json').read_text())['Replace']
report={'status':'running','scope':'Diagnostic observer only; no timing or cache safety claim. Repeats compare a partial state tuple within one resolveCall. JSX, this, rest and diagnostic-only applicability checks excluded. Counts include actual early exits. Repeated result compared to first result. Map cap 4096 per call; untracked requests can repeat omitted keys. Pointer retention can affect GC; normal-output controls do not prove full conformance.', 'baseHead':before['revision'],'baseSource':before['sha256'],'baselineSha256':sha(baseline),'candidateSha256':sha(candidate),'overlaySources':{str(Path(k).relative_to(root)):sha(v) for k,v in overlay.items()},'controllerSha256':sha(__file__),'runs':[]}
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ['GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOEXPERIMENT','NODE_OPTIONS','LD_PRELOAD']:env.pop(k,None)
env['TSC_TS_LIB_DIR']=str(root/'upstream/typescript-go/internal/bundled/libs')
def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
def inputs(p):
 assert sha(Path(p['cwd'])/p['args'][1])==p['configSha256']
 for f in p['preflight']['candidate']['inputs']:assert sha(Path(p['cwd'])/f['file'])==f['sha256']
try:
 for group in ['small','large']:
  ref=root/f'benchmarks/results/native-node-pointer/{group}.json';old=json.loads(ref.read_text());assert old['status']=='passed'
  for p in old['projects']:
   inputs(p);work=out/p['name'];work.mkdir(exist_ok=True)
   for mode in ['baseline','disabled','enabled']:
    binary=baseline if mode=='baseline' else candidate
    runenv=env|({'TSC_GO_ARGUMENT_REQUEST_CENSUS':str(work/'census.json')} if mode=='enabled' else {})
    command=[str(binary),*p['args']]
    r=subprocess.run(command,cwd=p['cwd'],env=runenv,capture_output=True,timeout=240)
    (work/(mode+'.stdout')).write_bytes(r.stdout);(work/(mode+'.stderr')).write_bytes(r.stderr)
    assert r.returncode==0 and r.stdout==b'' and r.stderr==b'',(p['name'],mode,r.returncode)
    counts=None
    if mode=='enabled':
     owners=json.loads((work/'census.json').read_text());assert owners
     counts={k:sum(o[k] for o in owners) for k in owners[0]}
     assert counts['Repeated']==counts['SameResult']+counts['DifferentResult'];assert counts['Repeated']+counts['Untracked']<=counts['Requests'];assert counts['BudgetChanged']<=counts['Requests']
    report['runs'].append({'project':p['name'],'mode':mode,'command':command,'cwd':p['cwd'],'referenceSha256':sha(ref),'inputCount':len(p['preflight']['candidate']['inputs']),'exitStatus':r.returncode,'stdoutSha256':sha(work/(mode+'.stdout')),'stderrSha256':sha(work/(mode+'.stderr')),'censusSha256':sha(work/'census.json') if counts else None,'counts':counts});save();print(p['name'],mode,counts,flush=True)
   inputs(p)
 assert sha(baseline)==report['baselineSha256'] and sha(candidate)==report['candidateSha256']
 after=source();assert (before['sha256'],before['revision'])==(after['sha256'],after['revision'])
 for k,v in overlay.items():assert sha(v)==report['overlaySources'][str(Path(k).relative_to(root))]
 report['status']='passed'
except Exception as e:report['status']='failed';report['error']=repr(e);raise
finally:save()
