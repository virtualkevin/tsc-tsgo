import pathlib,subprocess,json,hashlib,os
out=pathlib.Path('/tmp/tsc-relation-fixture-fix');root=pathlib.Path('/home/dev/tssss/tsc-tsgo');go='/tmp/tsc-toolchains/go/bin/go'
command=[go,'test','-json','-overlay',str(out/'baseline-overlay.json'),'./internal/checker','-run','^TestRelationKeys(RecursiveGenericAssignmentsAndDiagnostics|ColdRecursiveConstraints|RepeatedFailureDiagnosticsKeepUsePositions)$','-count=1']
def capture(label):
 js='import {captureGoSources} from "./scripts/build-provenance.mjs"; console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
 value=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root));(out/(label+'.json')).write_text(json.dumps(value));return {k:value[k] for k in ['sha256','revision','dirty']}
before=capture('main-source-before')
with (out/'baseline.jsonl').open('w') as stdout,(out/'baseline.stderr').open('w') as stderr:
 p=subprocess.run(command,cwd=root/'packages/tsc-go',env=os.environ|{'GOFLAGS':''},stdout=stdout,stderr=stderr)
after=capture('main-source-after')
report={'command':command,'cwd':str(root/'packages/tsc-go'),'environment':{'GOFLAGS':''},'exit_code':p.returncode,'main_source_before':before,'main_source_after':after,'main_unchanged':before['sha256']==after['sha256'],'baseline_revision':subprocess.check_output(['git','rev-parse','7437132'],cwd=root,text=True).strip(),'scope':'Three public API tests plus two cold-direction subtests, with old production checker.go/relater.go overlaid and candidate-private key tests disabled. No main source changes.','files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'baseline-overlay.json',out/'baseline-checker.go',out/'baseline-relater.go',out/'empty-internal-tests.go',out/'corrected.go',out/'baseline.jsonl',out/'baseline.stderr']}}
(out/'baseline-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(p.returncode)
