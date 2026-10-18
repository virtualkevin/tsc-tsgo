from pathlib import Path
import os,json,hashlib,subprocess
root=Path(__file__).resolve().parents[3]; out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
def source():return json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,text=True))
before=source(); assert before['sha256']=='216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd'
baseline=root/'packages/tsc-go/dist/tsc-go';candidate=Path('/tmp/tsc-name-construction-census')
assert sha(Path(str(baseline)+'.provenance.json'))=='76e6c4f05d244f4f3f1cd562950bbc3388716b139176ee3583ecc912e3a2bca2'
assert sha(baseline)=='8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f'
validation=json.loads((out/'validation.json').read_text());assert validation['passed'] and len(validation['runs'])==2
overlay=json.loads((out/'overlay.json').read_text())['Replace']
assert validation['overlaySources']=={k:sha(v) for k,v in overlay.items()}
build=json.loads((out/'build.json').read_text());assert sha(candidate)==build['binarySha256'] and build['overlaySources']==validation['overlaySources']
report={'status':'running','scope':'Construction-event census only; no timing, live-object, all-symbol-write, conversion-frequency or speedup claim. Includes temporary/repeated identifier, binder-symbol and checker-symbol constructor calls. Exact bytes, shared mutex and cloned names perturb execution. Bounded keys/bytes with untracked counts.', 'baseHead':before['revision'],'baseSource':before['sha256'],'baselineSha256':sha(baseline),'candidateSha256':sha(candidate),'overlaySources':{str(Path(k).relative_to(root)):sha(v) for k,v in overlay.items()},'controllerSha256':sha(__file__),'validationSha256':sha(out/'validation.json'),'runs':[]}
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
    runenv=env|({'TSC_GO_NAME_CONSTRUCTION_CENSUS':str(work/'census.json')} if mode=='enabled' else {})
    command=[str(binary),*p['args']]
    r=subprocess.run(command,cwd=p['cwd'],env=runenv,capture_output=True,timeout=600)
    (work/(mode+'.stdout')).write_bytes(r.stdout);(work/(mode+'.stderr')).write_bytes(r.stderr)
    assert r.returncode==0 and r.stdout==b'' and r.stderr==b'',(p['name'],mode,r.returncode)
    counts=None
    if mode=='enabled':
     census=json.loads((work/'census.json').read_text());counts=census['Counts']
     assert census['Labels']==['identifier-constructor','binder-symbol-constructor','checker-symbol-constructor']
     assert counts['LimitKeys']==1048576 and counts['LimitBytes']==67108864
     assert counts['Distinct']<=counts['LimitKeys'] and counts['DistinctBytes']<=counts['LimitBytes']
     masks=counts['MembershipMasks'];assert len(masks)==8 and masks[0]==0 and sum(masks)==counts['Distinct']
     assert len(counts['Categories'])==3
     for i,c in enumerate(counts['Categories']):
      assert len(c['LengthBuckets'])==65 and sum(c['LengthBuckets'])==c['Requests']
      assert c['Empty']==c['LengthBuckets'][0] and c['Distinct']+c['Untracked']<=c['Requests']
      assert c['Distinct']==sum(v for mask,v in enumerate(masks) if mask&(1<<i))
      assert c['DistinctBytes']<=counts['DistinctBytes'] and c['DistinctBytes']<=c['NameBytes']
    report['runs'].append({'project':p['name'],'mode':mode,'command':command,'cwd':p['cwd'],'referenceSha256':sha(ref),'inputCount':len(p['preflight']['candidate']['inputs']),'exitStatus':r.returncode,'stdoutSha256':sha(work/(mode+'.stdout')),'stderrSha256':sha(work/(mode+'.stderr')),'censusSha256':sha(work/'census.json') if counts else None,'counts':counts});save();print(p['name'],mode,None if counts is None else {'distinct':counts['Distinct'],'bytes':counts['DistinctBytes'],'categories':[(c['Requests'],c['Distinct'],c['Untracked']) for c in counts['Categories']]},flush=True)
   inputs(p)
 assert sha(baseline)==report['baselineSha256'] and sha(candidate)==report['candidateSha256']
 assert sha(Path(str(baseline)+'.provenance.json'))=='76e6c4f05d244f4f3f1cd562950bbc3388716b139176ee3583ecc912e3a2bca2'
 after=source();assert (before['sha256'],before['revision'])==(after['sha256'],after['revision'])
 for k,v in overlay.items():assert sha(v)==report['overlaySources'][str(Path(k).relative_to(root))]
 report['status']='passed'
except Exception as e:report['status']='failed';report['error']=repr(e);raise
finally:save()
