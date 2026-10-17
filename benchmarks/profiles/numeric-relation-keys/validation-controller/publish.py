import argparse,pathlib,json,hashlib
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--repo',default='/home/dev/tssss/tsc-tsgo');args=ap.parse_args()
root=pathlib.Path(args.repo);output=pathlib.Path(args.output);report=json.loads((output/'validation.json').read_text())
assert report['source_unchanged'] and not report['validation_incomplete']
assert report['source_before']['sha256']==report['expected_source_sha256']
assert len(report['processes'])==5 and all(r['exit_code']==0 for r in report['processes'])
common={k:report[k] for k in ['schema_version','toolchain','fixture_revisions','source_before','source_after','source_unchanged','source_scope','source_file_count','expected_source_sha256','coverage_limits']}
common['controller_report_sha256']=hashlib.sha256((output/'validation.json').read_bytes()).hexdigest()
common['controller_report_path']=str(output/'validation.json')
common['duration_note']='Correctness validation may overlap builds; durations are not performance measurements.'
focused=common|{'scope':'Seven numeric-relation tests (two cold-direction subtests) in normal, race and checkptr modes; no claim of actual complexity/stack overflow generation coverage.','suites':{k:v for k,v in report['suites'].items() if k in ['focused','race','checkptr']},'processes':[r for r in report['processes'] if r['name'] in ['focused','race','checkptr']]}
focused['fixture_correction_baseline']=json.loads(pathlib.Path('/tmp/tsc-relation-fixture-fix/baseline-result.json').read_text())
baseline_events=[json.loads(line) for line in pathlib.Path('/tmp/tsc-relation-fixture-fix/baseline.jsonl').read_text().splitlines() if line.startswith('{')]
focused['fixture_correction_baseline']['test_records']={a:sum(e.get('Test') is not None and e['Action']==a for e in baseline_events) for a in ['pass','skip','fail']}
focused['fixture_correction_archive']='benchmarks/profiles/numeric-relation-keys/fixture-correction/'
focused['fixture_correction_patch_sha256']=hashlib.sha256(pathlib.Path('/tmp/tsc-relation-fixture-fix/fixture-fix.patch').read_bytes()).hexdigest()
focused['initial_failed_fixture_report']='benchmarks/validation/numeric-relation-initial-focused-failure.json'
conformance=common|{'scope':'Root npm ten-package test alias and full pinned upstream conformance on numeric relation source.','suites':{k:v for k,v in report['suites'].items() if k in ['root-npm','conformance']},'processes':[r for r in report['processes'] if r['name'] in ['root-npm','conformance']],'focused_report':'benchmarks/validation/numeric-relation-focused.json'}
for name,value in [('focused',focused),('conformance',conformance)]:
 (root/'benchmarks/validation'/('numeric-relation-'+name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps({k:{'records':v['test_records'],'packages':len(v['package_status']),'cases':v.get('source_configuration_cases')} for k,v in report['suites'].items()}))
