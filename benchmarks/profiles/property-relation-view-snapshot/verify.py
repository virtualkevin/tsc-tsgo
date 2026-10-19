"""Read raw validation evidence independently; require completed CLI checks too."""
from pathlib import Path
import gzip,hashlib,json,re,importlib.util,tempfile
p=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
sources={k:sha(Path(v).read_bytes()) for k,v in json.loads((p/'overlay.json').read_text())['Replace'].items()}
focused=json.loads((p/'validation.json').read_text());assert focused['status']=='passed' and focused['sources']==sources
expected={'TestPropertyViewMetadataAndIdentity','TestPropertyViewFrozenDecisionAndRetirement','TestPropertyViewFallbackBeforeEffects','TestPropertyViewIndependentHistories','TestPropertyViewTypeCacheTransfer','TestPropertyViewReentrantTypeMaterialization','TestPropertyViewTypeIndependentHistories','TestPropertyViewNestedQueryAssignment','TestPropertyViewPanicHistory','TestPropertyViewRelationDifferential','TestPropertyViewRelationFallbackBeforeQueries','TestPropertyViewPresenceSnapshot'}
for mode in ['normal','race','checkptr']:
 events=[json.loads(x) for x in (p/(mode+'.stdout')).read_text().splitlines()]
 assert {e['Test'] for e in events if e['Action']=='pass' and 'Test' in e}==expected
 assert not any(e['Action'] in ['fail','skip'] for e in events)
full=json.loads((p/'full-validation.json').read_text());assert full['passed'] and full['sources']==sources
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
    assert len([e for e in events if e['Action']=='pass' and 'Test' in e])=={'root':21187,'services':219}[run['name']]
helper=p.parents[2]/'benchmarks/profiles/prehashed-relations-512/validation-controller/validate.py'
assert sha(helper.read_bytes())==full['helperSha256']
spec=importlib.util.spec_from_file_location('conformance_readback',helper)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
run=next(r for r in full['runs'] if r['name']=='conformance')
with tempfile.TemporaryDirectory(prefix='property-view-conformance-readback-') as temporary:
 copy=dict(run)
 for stream in ['stdout','stderr']:
  raw=Path(run[stream]);target=Path(temporary)/raw.name
  target.write_bytes(gzip.decompress(raw.with_suffix(raw.suffix+'.gz').read_bytes()))
  copy[stream]=str(target)
 summary=module.summarize_run(copy)
 assert not summary['integrity_errors']
 assert summary['source_configuration_cases']=={'total':14915,'fully_checked':12789,'partially_checked':8,'unsupported_skipped':2118,'failed':0}
cli=json.loads((p/'final-cli.json').read_text())
assert not cli['passed'] and cli['error']=="KeyboardInterrupt('15')"
assert [r['mode'] for r in cli['runs']]==['normal','integration']
remaining=json.loads((p/'final-cli-remaining.json').read_text());assert remaining['passed']
assert [r['mode'] for r in remaining['runs']]==['race','checkptr']
for report in [cli,remaining]:
 assert report['freezeSha256']==sha((p/'cli-freeze.json').read_bytes())
 assert report['commonSha256']==sha((p/'final_common.py').read_bytes())
 assert report['normalBuildSha256']==sha((p/'build.json').read_bytes())
assert cli['comparators']==remaining['comparators']
interrupted=json.loads((p/'interrupted.json').read_text())
for f in interrupted['files']:
 data=(p/f['file']).read_bytes()
 assert sha(data)==f['sha256'] and sha(gzip.decompress(data))==f['rawSha256']
for run in cli['runs']+remaining['runs']:
 assert run['passed'] and run['exitCode']==0
 expected_count=12 if run['mode']=='integration' else 80
 assert run['counts']=={'tests':expected_count,'pass':expected_count,'fail':0,'cancelled':0,'skipped':0,'todo':0}
 log=run['log'];archive=p/('remaining-cli-logs' if run['mode'] in ['race','checkptr'] else 'final-cli-logs')/log['file']
 data=gzip.decompress(archive.read_bytes())
 assert sha(archive.read_bytes())==log['sha256'] and sha(data)==log['rawSha256']
 text=re.sub(r'\x1b\[[0-9;]*m','',data.decode())
 assert {k:int(v) for k,v in re.findall(r'^(?:ℹ\s*)?(tests|pass|fail|cancelled|skipped|todo)\s+(\d+)\s*$',text,re.M)}==run['counts']
(p/'readback.json').write_text(json.dumps({'passed':True,'sources':sources,'evidence':{f:sha((p/f).read_bytes()) for f in ['validation.json','full-validation.json','final-cli.json','final-cli-remaining.json','interrupted.json']}},indent=2)+'\n')
print('Independent evidence readback passed')
