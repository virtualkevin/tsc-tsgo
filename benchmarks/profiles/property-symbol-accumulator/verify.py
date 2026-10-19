"""Read raw validation evidence independently; require completed CLI checks too."""
from pathlib import Path
import gzip,hashlib,json,re,importlib.util,tempfile,sys
sys.dont_write_bytecode=True
p=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
sources={k:sha(Path(v).read_bytes()) for k,v in json.loads((p/'candidate-overlay.json').read_text())['Replace'].items()}
focused=json.loads((p/'validation.json').read_text());assert focused['passed']
assert focused['sources']=={str(Path(v)):sha(Path(v).read_bytes()) for v in json.loads((p/'candidate-overlay.json').read_text())['Replace'].values()}
expected={'TestPropertyAccumulatorQueryOrder', 'TestUnionPropertyCachePreservesRecursiveAugmentedWinner', 'TestUnionPropertyCacheSharesCompleteResultIdentity', 'TestUnionPropertyCacheMissDoesNotCacheAbsence', 'TestUnionPropertyCachePreservesReentrantPopulation', 'TestUnionPropertyCacheKeepsAugmentedPrecedence', 'TestUnionPropertyCacheDoesNotReusePartialResults', 'TestUnionPropertyCacheSameSymbolRecursiveOverwritePreservesIdentity'}
assert [r['name'] for r in focused['runs']]==[v+'-'+m for v in ['baseline','candidate'] for m in ['normal','race','checkptr']]
for run in focused['runs']:
 assert run['passed'] and run['exitCode']==0
 events=[json.loads(x) for x in (p/(run['name']+'.stdout')).read_text().splitlines()]
 assert {e['Test'] for e in events if e['Action']=='pass' and 'Test' in e}==expected
 assert not any(e['Action'] in ['fail','skip'] for e in events)
full=json.loads((p/'full-validation.json').read_text());assert full['passed'] and full['sources']==sources
assert full['controllerSha256']==sha((p/'validate-full.py').read_bytes())
assert [r['name'] for r in full['runs']]==['root','services','conformance']
for run in full['runs']:
 assert run['passed'] and run['exit_code']==0
 for stream in ['stdout','stderr']:
  raw=Path(run[stream]);archive=raw.with_suffix(raw.suffix+'.gz');data=gzip.decompress(archive.read_bytes())
  assert sha(archive.read_bytes())==run['archive'][archive.name]
  assert sha(data)==run[stream+'_sha256']
  if stream=='stdout':
   events=[json.loads(x) for x in data.splitlines()]
   assert not any(e['Action']=='fail' for e in events)
   if run['name']!='conformance':
    assert len([e for e in events if e['Action']=='pass' and 'Test' in e])=={'root':21176,'services':219}[run['name']]
helper=p.parents[2]/'benchmarks/profiles/prehashed-relations-512/validation-controller/validate.py'
assert sha(helper.read_bytes())==full['helperSha256']
spec=importlib.util.spec_from_file_location('conformance_readback',helper)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
run=next(r for r in full['runs'] if r['name']=='conformance')
with tempfile.TemporaryDirectory(prefix='property-accumulator-conformance-readback-') as temporary:
 copy=dict(run)
 for stream in ['stdout','stderr']:
  raw=Path(run[stream]);target=Path(temporary)/raw.name
  target.write_bytes(gzip.decompress(raw.with_suffix(raw.suffix+'.gz').read_bytes()))
  copy[stream]=str(target)
 summary=module.summarize_run(copy)
 assert not summary['integrity_errors']
 assert summary['source_configuration_cases']=={'total':14915,'fully_checked':12789,'partially_checked':8,'unsupported_skipped':2118,'failed':0}
cli=json.loads((p/'final-cli-resumed.json').read_text())
original=json.loads((p/'final-cli.json').read_text())
assert not original['passed'] and original['error']=="KeyboardInterrupt('15')"
assert original['controllerSha256']==sha((p/'validate-cli.py').read_bytes())
assert cli['originalReportSha256']==sha((p/'final-cli.json').read_bytes())
assert cli['runs'][:2]==original['runs']
for key in ['freezeSha256','commonSha256','normalBuildSha256','comparators']:assert cli[key]==original[key]
assert cli['passed']
assert [r['mode'] for r in cli['runs']]==['normal','integration','race','checkptr']
assert cli['freezeSha256']==sha((p/'cli-freeze.json').read_bytes())
assert cli['commonSha256']==sha((p/'final_common.py').read_bytes())
assert cli['normalBuildSha256']==sha((p/'build.json').read_bytes())
assert cli['controllerSha256']==sha((p/'validate-cli-remaining.py').read_bytes())
for run in cli['runs']:
 assert run['passed'] and run['exitCode']==0
 expected_count=12 if run['mode']=='integration' else 80
 assert run['counts']=={'tests':expected_count,'pass':expected_count,'fail':0,'cancelled':0,'skipped':0,'todo':0}
 log=run['log'];archive=p/'final-cli-logs'/log['file']
 data=gzip.decompress(archive.read_bytes())
 assert sha(archive.read_bytes())==log['sha256'] and sha(data)==log['rawSha256']
 text=re.sub(r'\x1b\[[0-9;]*m','',data.decode())
 assert {k:int(v) for k,v in re.findall(r'^(?:ℹ\s*)?(tests|pass|fail|cancelled|skipped|todo)\s+(\d+)\s*$',text,re.M)}==run['counts']
(p/'readback.json').write_text(json.dumps({'passed':True,'sources':sources,'evidence':{f:sha((p/f).read_bytes()) for f in ['validation.json','full-validation.json','final-cli.json','final-cli-resumed.json']}},indent=2)+'\n')
print('Independent evidence readback passed')
