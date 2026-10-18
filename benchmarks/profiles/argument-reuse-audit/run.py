from pathlib import Path
import os,subprocess,json,hashlib
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
def capture():return json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,text=True))
before=capture();assert before['sha256']=='216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd'
virtual=root/'packages/tsc-go/internal/checker/argument_reuse_audit_test.go';assert not virtual.exists()
overlay={'Replace':{str(virtual):str(out/'argument_reuse_audit_test.go')}};(out/'overlay.json').write_text(json.dumps(overlay,indent=2)+'\n')
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','GOOS','GOARCH','GOAMD64','GOCOVERDIR']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
command=['/tmp/tsc-toolchains/go/bin/go','test','-json','-overlay',str(out/'overlay.json'),'./internal/checker','-run','^TestArgumentReuseAudit','-count=1','-timeout','10m']
with (out/'tests.jsonl').open('w') as o,(out/'tests.stderr').open('w') as e:code=subprocess.run(command,cwd=root/'packages/tsc-go',env=env,stdout=o,stderr=e,timeout=900).returncode
after=capture();assert (before['sha256'],before['revision'])==(after['sha256'],after['revision']);assert not virtual.exists()
events=[json.loads(l) for l in (out/'tests.jsonl').read_text().splitlines()];terminal=[e for e in events if e['Action'] in ['pass','fail','skip']];tests=[e for e in terminal if e.get('Test')]
passed=code==0 and len(tests)==2 and all(e['Action']=='pass' for e in terminal)
report={'passed':passed,'exitCode':code,'command':command,'baseSource':before['sha256'],'baseHead':before['revision'],'testSourceSha256':sha(out/'argument_reuse_audit_test.go'),'stdoutSha256':sha(out/'tests.jsonl'),'stderrSha256':sha(out/'tests.stderr'),'tests':[(e['Test'],e['Action']) for e in tests],'sourceHashes':{n:sha(root/n) for n in ['packages/tsc-go/internal/checker/checker.go','packages/tsc-go/internal/checker/lazy_properties_test.go','packages/tsc-go/internal/checker/pending_members_test.go']},'scope':'Focused semantic boundary tests through an overlay only; no production source change, full new conformance claim or timing.'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(0 if passed else 1)
