"""Read back completed candidate evidence before building production provenance."""
import difflib,gzip,importlib.util,json,re,sys
sys.dont_write_bytecode=True
from final_common import *
verify()
go=json.loads((PROFILE/'validation.json').read_text())
cli=json.loads((PROFILE/'final-cli.json').read_text())
assert not go['passed'] and go['error']=="KeyboardInterrupt('15')"
assert not cli['passed'] and cli['error']=="KeyboardInterrupt('15')"
assert [x['name'] for x in go['runs']]==['normal','race','checkptr']
assert [x['mode'] for x in cli['runs']]==['normal','integration']
remaining=json.loads((PROFILE/'validation-remaining.json').read_text())
cli_remaining=json.loads((PROFILE/'final-cli-remaining.json').read_text())
assert remaining['passed'] and cli_remaining['passed']
assert remaining['controllerSha256']==sha(PROFILE/'validate-remaining.py')
for key in ['head','sources','pins','helperSha256']:assert remaining[key]==go[key]
assert [x['name'] for x in remaining['runs']]==['root','services','conformance']
assert cli_remaining['controllerSha256']==sha(PROFILE/'validate-cli-remaining.py')
for key in ['commonSha256','freezeSha256','normalBuildSha256','comparators']:assert cli_remaining[key]==cli[key]
assert [x['mode'] for x in cli_remaining['runs']]==['race','checkptr']
interrupted=json.loads((PROFILE/'interrupted.json').read_text())
for original,entry in interrupted['files'].items():
 archived=PROFILE/entry['archive'];assert sha(archived)==entry['sha256']
 import hashlib
 assert hashlib.sha256(gzip.decompress(archived.read_bytes())).hexdigest()==entry['rawSha256']
 if original.endswith(('validation.json','final-cli.json')):assert sha(original)==entry['rawSha256']
go['runs']+=remaining['runs'];cli['runs']+=cli_remaining['runs']
assert go['head']==FREEZE['head'] and go['sources']==FREEZE['sources']
assert go['controllerSha256']==sha(PROFILE/'validate.py')
assert cli['controllerSha256']==sha(PROFILE/'validate-cli.py') and cli['commonSha256']==sha(PROFILE/'final_common.py')
assert cli['freezeSha256']==sha(PROFILE/'cli-freeze.json')
assert cli['normalBuildSha256']==sha(PROFILE/'build.json')
helper=ROOT/'benchmarks/profiles/prehashed-relations-512/validation-controller/validate.py'
assert sha(helper)==go['helperSha256']
spec=importlib.util.spec_from_file_location('conformance_summary',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
assert [x['name'] for x in go['runs']]==['normal','race','checkptr','root','services','conformance']
expected_focused={'TestMergedSubstitutionExhaustive','TestMergedSubstitutionEligibilityAndEffects','TestMergedSubstitutionConcurrentReads','TestMergedSubstitutionOriginalRoots'}
summary={}
for run in go['runs']:
 assert run['passed'] and run['exit_code']==0
 for stream in ['stdout','stderr']:
  raw=Path(run[stream]);assert sha(raw)==run[stream+'_sha256']
  archived=raw.with_suffix(raw.suffix+'.gz')
  assert sha(archived)==run['archive'][archived.name]
  assert gzip.decompress(archived.read_bytes())==raw.read_bytes()
 events=[json.loads(x) for x in Path(run['stdout']).read_text().splitlines()]
 tests=[x for x in events if x.get('Action')=='pass' and 'Test' in x]
 if run['name']=='conformance':
  current=mod.summarize_run(run)
  assert current==run['summary']
  assert current['source_configuration_cases']=={'total':14915,'fully_checked':12789,'partially_checked':8,'unsupported_skipped':2118,'failed':0}
  summary[run['name']]=current['source_configuration_cases']
 else:
  assert not any(x.get('Action') in ('fail','skip') and 'Test' in x for x in events)
  if run['name'] in ('normal','race','checkptr'):assert {x['Test'] for x in tests}==expected_focused
  if run['name']=='root':assert len(tests)==21179 and expected_focused.issubset({x['Test'] for x in tests})
  if run['name']=='services':assert len(tests)==219
  summary[run['name']]=len(tests)
assert [x['mode'] for x in cli['runs']]==['normal','integration','race','checkptr']
for run in cli['runs']:
 assert run['passed'] and run['exitCode']==0
 expected=12 if run['mode']=='integration' else 80
 for archive in [run['log']]+([run['buildLog']] if 'buildLog' in run else []):
  archive_dir='remaining-cli-logs' if run['mode'] in ['race','checkptr'] else 'final-cli-logs'
  path=PROFILE/archive_dir/archive['file']
  assert sha(path)==archive['sha256']
  import hashlib
  assert hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()==archive['rawSha256']
 text=re.sub(r'\x1b\[[0-9;]*m','',gzip.decompress((PROFILE/archive_dir/run['log']['file']).read_bytes()).decode())
 counts={k:int(v) for k,v in re.findall(r'^(?:ℹ\s*)?(tests|pass|fail|cancelled|skipped|todo)\s+(\d+)\s*$',text,re.M)}
 assert counts==run['counts']=={'tests':expected,'pass':expected,'fail':0,'cancelled':0,'skipped':0,'todo':0}
 summary['cli-'+run['mode']]=expected
for name,digest in cli['comparators'].items():assert sha(name)==digest
build=json.loads((PROFILE/'build.json').read_text())
assert build['sources']==FREEZE['sources'] and build['exitCode']==0
assert sha(OUT/'tsc-merged-substitution')==build['binarySha256']
# Independently regenerate all overlay additions and changes, including tests.
patch=[]
for destination,staged in json.loads(OVERLAY.read_text())['Replace'].items():
 old=Path(destination);new=Path(staged)
 patch+=difflib.unified_diff(old.read_text().splitlines(True) if old.exists() else [],new.read_text().splitlines(True),fromfile=str(old.relative_to(ROOT)) if old.exists() else '/dev/null',tofile=str(old.relative_to(ROOT)))
assert ''.join(patch)==(PROFILE/'candidate.patch').read_text()
(PROFILE/'validation-readback.json').write_text(json.dumps({'passed':True,'summary':summary,'binarySha256':build['binarySha256'],'sourceFiles':len(FREEZE['sources']),'verifierSha256':sha(__file__)},indent=2)+'\n')
print(json.dumps(summary,indent=2))
