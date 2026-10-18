from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3];out=Path('/tmp/tsc-parser-interner');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
originalPath=out/'units/validation.json';original=json.loads(originalPath.read_text());repairPath=out/'parser-repair/validation.json';repair=json.loads(repairPath.read_text())
expected='1e5399a8058a1b41ef613763afec4801bfcfd703ad7ae6616458eb5d590ffba8';parser='github.com/microsoft/typescript-go/internal/parser'
assert not original['passed'] and repair['passed'] and repair['sourceAndFixturesUnchanged']
assert original['sourceSha256']==repair['sourceSha256']==expected and original['head']==repair['head']
assert len(original['runs'])==3
for run in original['runs']:
 path=out/'units';assert sha(path/(run['name']+'.jsonl'))==run['stdoutSha256'];assert sha(path/(run['name']+'.stderr'))==run['stderrSha256']
 if run['name']!='root':assert run['passed'] and run['exitCode']==0
run=original['runs'][-1];assert run['name']=='root' and run['exitCode']==1
events=[json.loads(x) for x in (out/'units/root.jsonl').read_text().splitlines()];term=[e for e in events if e['Action'] in ['pass','skip','fail']]
bad=[(e['Package'],e.get('Test'),e['Action']) for e in term if e['Action']!='pass'];assert sorted(bad,key=str)==sorted([(parser,'FuzzParser','fail'),(parser,None,'fail')],key=str)
assert any(e.get('Test')=='FuzzParser' and 'lstat ' in e.get('Output','') and '/TypeScript/src: no such file or directory' in e['Output'] for e in events)
assert len(run['packages'])==12 and all(v=='pass' for k,v in run['packages'].items() if k!=parser)
for filename,key in [('parser.jsonl','stdoutSha256'),('parser.stderr','stderrSha256'),('fixtures.json','fixtureManifestSha256')]:assert sha(out/'parser-repair'/filename)==repair[key]
repaired=[json.loads(x) for x in (out/'parser-repair/parser.jsonl').read_text().splitlines()];rt=[e for e in repaired if e['Action'] in ['pass','skip','fail']];assert len([e for e in rt if e.get('Test')])==18056 and all(e['Action']=='pass' and e['Package']==parser for e in rt)
assert any(e['Action']=='pass' and not e.get('Test') for e in rt)
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
current=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,text=True));assert current['sha256']==expected and current['revision']==original['head']
report={'passed':True,'sourceSha256':expected,'head':original['head'],'controllerSha256':sha(__file__),'originalReportSha256':sha(originalPath),'repairReportSha256':sha(repairPath),'scope':'Composite validation: original race/checkptr and 11 passing root packages plus parser-only rerun after pinned fixture expansion. Original root exit1 and FuzzParser setup failure remain unmodified; no compiler source changes.','originalPassingRootTestRecords':len([e for e in term if e.get('Test') and e['Action']=='pass']),'repairedParserTestRecords':repair['tests'],'runs':original['runs'],'repairedParser':repair}
(out/'units/verified.json').write_text(json.dumps(report,indent=2)+'\n');print(report['originalPassingRootTestRecords'],report['repairedParserTestRecords'])
