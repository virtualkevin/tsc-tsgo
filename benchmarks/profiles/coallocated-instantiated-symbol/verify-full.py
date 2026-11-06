from pathlib import Path
import gzip,hashlib,json,re,importlib.util,tempfile,subprocess,sys
sys.dont_write_bytecode=True
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
sources={k:sha(v) for k,v in json.loads((p/'overlay.json').read_text())['Replace'].items()}
subprocess.run([sys.executable,str(p/'verify-focused.py')],check=True)
subprocess.run([sys.executable,str(p/'source-audit.py')],check=True)
full=json.loads((p/'full-validation.json').read_text());assert full['passed'] and full['sources']==sources
assert full['controllerSha256']==sha(p/'validate-full.py')
assert [r['name'] for r in full['runs']]==['root','services','conformance']
for run in full['runs']:
 assert run['passed'] and run['exit_code']==0
 for stream in ['stdout','stderr']:
  raw=Path(run[stream]);archive=raw.with_suffix(raw.suffix+'.gz');data=gzip.decompress(archive.read_bytes())
  assert sha(archive)==run['archive'][archive.name] and hashlib.sha256(data).hexdigest()==run[stream+'_sha256']
  if stream=='stdout':
   events=[json.loads(x) for x in data.splitlines()]
   assert not any(e.get('Action') in ['fail','build-fail'] for e in events)
   if run['name']!='conformance':assert len([e for e in events if e.get('Action')=='pass' and 'Test' in e])=={'root':21177,'services':219}[run['name']]
helper=p.parents[2]/'benchmarks/profiles/prehashed-relations-512/validation-controller/validate.py';assert sha(helper)==full['helperSha256']
spec=importlib.util.spec_from_file_location('conformance_readback',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
run=full['runs'][2]
with tempfile.TemporaryDirectory(prefix='coallocated-symbol-readback-') as temporary:
 copy=dict(run)
 for stream in ['stdout','stderr']:
  raw=Path(run[stream]);target=Path(temporary)/raw.name;target.write_bytes(gzip.decompress(raw.with_suffix(raw.suffix+'.gz').read_bytes()));copy[stream]=str(target)
 summary=module.summarize_run(copy)
 assert not summary['integrity_errors'] and summary['source_configuration_cases']=={'total':14915,'fully_checked':12789,'partially_checked':8,'unsupported_skipped':2118,'failed':0}

(p/'full-readback.json').write_text(json.dumps({'passed':True,'fullReportSha256':sha(p/'full-validation.json'),'verifierSha256':sha(__file__),'sources':sources},indent=2)+'\n')
print('Full compiler/services/conformance raw readback passed')
