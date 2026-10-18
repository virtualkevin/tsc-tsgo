from pathlib import Path
import hashlib,json,os,subprocess
r=Path('/home/dev/tssss/tsc-tsgo');out=Path('/tmp/tsc-parser-interner/parser-repair');out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
def capture():return json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=r,text=True))
before=capture();assert before['sha256']=='1e5399a8058a1b41ef613763afec4801bfcfd703ad7ae6616458eb5d590ffba8'
upstream=r/'upstream/TypeScript';pin=subprocess.check_output(['git','rev-parse','HEAD'],cwd=upstream,text=True).strip();assert pin=='4d4f005c8541e0255a9d8791205fdce326e462bc'
fixtures={str(p.relative_to(upstream)):sha(p) for folder in ['src','scripts'] for p in sorted((upstream/folder).rglob('*')) if p.is_file()};assert fixtures
(out/'fixtures.json').write_text(json.dumps({'revision':pin,'files':fixtures},indent=2)+'\n')
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
command=['/tmp/tsc-toolchains/go/bin/go','test','-json','./internal/parser','-count=1','-timeout','20m']
with (out/'parser.jsonl').open('w') as a,(out/'parser.stderr').open('w') as b:code=subprocess.run(command,cwd=r/'packages/tsc-go',env=env,stdout=a,stderr=b,timeout=1500).returncode
events=[json.loads(line) for line in (out/'parser.jsonl').read_text().splitlines()];terminal=[e for e in events if e['Action'] in ['pass','fail','skip']];tests=[e for e in terminal if e.get('Test')];skips=[e for e in tests if e['Action']=='skip']
after=capture();unchanged=(before['sha256'],before['revision'])==(after['sha256'],after['revision']) and all(sha(upstream/p)==h for p,h in fixtures.items())
report={'passed':code==0 and unchanged and all(e['Action']=='pass' for e in terminal),'sourceSha256':before['sha256'],'head':before['revision'],'command':command,'exitCode':code,'tests':len(tests),'skips':skips,'stdoutSha256':sha(out/'parser.jsonl'),'stderrSha256':sha(out/'parser.stderr'),'fixtureManifestSha256':sha(out/'fixtures.json'),'controllerSha256':sha(__file__),'sourceAndFixturesUnchanged':unchanged}
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
raise SystemExit(0 if report['passed'] else 1)
