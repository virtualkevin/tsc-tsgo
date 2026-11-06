"""Read raw validation evidence independently; require completed CLI checks too."""
from pathlib import Path
import gzip,hashlib,json,re,importlib.util,tempfile,sys
sys.dont_write_bytecode=True
p=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
sources={k:sha(Path(v).read_bytes()) for k,v in json.loads((p/'overlay.json').read_text())['Replace'].items()}
focused=json.loads((p/'validation.json').read_text());assert focused['status']=='passed' and focused['sources']==sources
expected={'TestOptionalSymbolStorageHistory','TestOptionalSymbolStorageLazyAndRetainedSlots','TestOptionalSymbolStorageLayout','TestOptionalSymbolStorageCheckerClone'}
assert [r['name'] for r in focused['results']]==['normal','race','checkptr']
for run in focused['results']:
 assert run['exitCode']==0 and set(run['passed'])==expected
 events=[json.loads(x) for x in (p/(run['name']+'.stdout')).read_text().splitlines()]
 assert {e['Test'] for e in events if e['Action']=='pass' and 'Test' in e}==expected
 assert not any(e['Action'] in ['fail','skip'] for e in events)
baseline=json.loads((p/'baseline-validation.json').read_text());assert baseline['status']=='passed'
assert baseline['sources']=={k:sha(Path(v).read_bytes()) for k,v in json.loads((p/'baseline-overlay.json').read_text())['Replace'].items()}
assert [r['name'] for r in baseline['results']]==['normal','race','checkptr']
for run in baseline['results']:
 assert run['exitCode']==0 and run['passed']==['TestOptionalSymbolStorageCheckerClone']
 events=[json.loads(x) for x in (p/('baseline-'+run['name']+'.stdout')).read_text().splitlines()]
 assert [e['Test'] for e in events if e['Action']=='pass' and 'Test' in e]==run['passed']
 assert not any(e['Action'] in ['fail','skip'] for e in events)
failure=json.loads((p/'failed-fixture/failure.json').read_text());assert not failure['passed'] and failure['exitCode']==1
for name,digest in failure['artifacts'].items():assert sha((p/'failed-fixture'/name).read_bytes())==digest
for path,digest in failure['sources'].items():
 if not path.endswith('/optional_symbol_clone_test.go'):assert sources[path]==digest
 else:assert sha((p/'failed-fixture/optional_symbol_clone_test.go').read_bytes())==digest
import subprocess
subprocess.run([sys.executable,str(p/'source-audit.py')],check=True)
disk=json.loads((p/'failed-disk/failure.json').read_text())
for name,digest in disk['files'].items():assert sha((p/name).read_bytes())==digest
assert disk['sources']==sources
assert sha((p/'cache-cleanup.json').read_bytes())==disk['cleanupSha256']
full=json.loads((p/'full-validation-resumed.json').read_text());assert full['passed'] and full['sources']==sources
assert full['previousReportSha256']==sha((p/'full-validation.json').read_bytes())
assert full['controllerSha256']==sha((p/'validate-full-resumed.py').read_bytes())
assert full['previousInterruptedReportSha256']==sha((p/'full-validation-after-cache-cleanup.json').read_bytes())
previous=json.loads((p/'full-validation-after-cache-cleanup.json').read_text())
assert previous['controllerSha256']==sha((p/'validate-full-after-cache-cleanup.py').read_bytes())
assert full['runs'][:2]==previous['runs']
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
    assert len([e for e in events if e['Action']=='pass' and 'Test' in e])=={'root':21179,'services':219}[run['name']]
helper=p.parents[2]/'benchmarks/profiles/prehashed-relations-512/validation-controller/validate.py'
assert sha(helper.read_bytes())==full['helperSha256']
spec=importlib.util.spec_from_file_location('conformance_readback',helper)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
run=next(r for r in full['runs'] if r['name']=='conformance')
with tempfile.TemporaryDirectory(prefix='optional-symbol-conformance-readback-') as temporary:
 copy=dict(run)
 for stream in ['stdout','stderr']:
  raw=Path(run[stream]);target=Path(temporary)/raw.name
  target.write_bytes(gzip.decompress(raw.with_suffix(raw.suffix+'.gz').read_bytes()))
  copy[stream]=str(target)
 summary=module.summarize_run(copy)
 assert not summary['integrity_errors']
 assert summary['source_configuration_cases']=={'total':14915,'fully_checked':12789,'partially_checked':8,'unsupported_skipped':2118,'failed':0}
cli=json.loads((p/'final-cli.json').read_text())
assert cli['previousFailureSha256']==sha((p/'failed-disk/failure.json').read_bytes())
assert cli['passed']
assert [r['mode'] for r in cli['runs']]==['normal','integration','race','checkptr']
assert cli['freezeSha256']==sha((p/'cli-freeze.json').read_bytes())
assert cli['commonSha256']==sha((p/'final_common.py').read_bytes())
assert cli['normalBuildSha256']==sha((p/'build-after-cache-cleanup.json').read_bytes())
assert cli['controllerSha256']==sha((p/'validate-cli-after-cache-cleanup.py').read_bytes())
for run in cli['runs']:
 assert run['passed'] and run['exitCode']==0
 expected_count=12 if run['mode']=='integration' else 80
 assert run['counts']=={'tests':expected_count,'pass':expected_count,'fail':0,'cancelled':0,'skipped':0,'todo':0}
 log=run['log'];archive=p/'final-cli-logs'/log['file']
 data=gzip.decompress(archive.read_bytes())
 assert sha(archive.read_bytes())==log['sha256'] and sha(data)==log['rawSha256']
 text=re.sub(r'\x1b\[[0-9;]*m','',data.decode())
 assert {k:int(v) for k,v in re.findall(r'^(?:ℹ\s*)?(tests|pass|fail|cancelled|skipped|todo)\s+(\d+)\s*$',text,re.M)}==run['counts']
(p/'readback.json').write_text(json.dumps({'passed':True,'sources':sources,'evidence':{f:sha((p/f).read_bytes()) for f in ['validation.json','baseline-validation.json','source-audit.json','full-validation-resumed.json','full-validation-after-cache-cleanup.json','final-cli.json','failed-disk/failure.json']}},indent=2)+'\n')
print('Independent evidence readback passed')
