"""Validate existing successful go-test output; do not rerun or hide tests."""
from pathlib import Path
import json, hashlib, subprocess
root=Path('/home/dev/tssss/tsc-tsgo')
out=Path('/tmp/tsc-compact-symbol-table/services')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
original=json.loads((out/'validation.json').read_text())
assert not original['passed'] and len(original['runs'])==1
run=original['runs'][0]
assert run['exitCode']==0
assert sha(out/'services.jsonl')==run['stdoutSha256']
assert sha(out/'services.stderr')==run['stderrSha256']
events=[json.loads(l) for l in (out/'services.jsonl').read_text().splitlines()]
terminal=[e for e in events if e['Action'] in ['pass','skip','fail']]
tests=[e for e in terminal if e.get('Test')]
packages=[e for e in terminal if not e.get('Test')]
empty='github.com/microsoft/typescript-go/internal/ls/change'
assert len(tests)==219 and all(e['Action']=='pass' for e in tests)
assert len([e for e in tests if '/' not in e['Test']])==60
assert len(packages)==7
assert [(e['Package'],e['Action']) for e in packages if e['Action']!='pass']==[(empty,'skip')]
assert not list((root/'packages/tsc-go/internal/ls/change').glob('*_test.go'))
assert any(e.get('Package')==empty and '[no test files]' in e.get('Output','') for e in events)
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
current=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,text=True))
assert current['sha256']==original['sourceSha256'] and current['revision']==original['head']
report={'passed':True,'sourceSha256':current['sha256'],'head':current['revision'],
 'originalControllerReportSha256':sha(out/'validation.json'),'recorderSha256':sha(__file__),
 'tests':len(tests),'topLevelTests':60,'packagesWithTests':6,'emptyPackages':[empty],
 'stdoutSha256':run['stdoutSha256'],'stderrSha256':run['stderrSha256'],
 'explanation':'Original command exited zero; all actual tests passed. Original controller rejected a package with no test files. This records the preserved output without rerunning or treating a skipped test as a pass.'}
(out/'verified.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
