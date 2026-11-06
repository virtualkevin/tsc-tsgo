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
   if run['name']!='conformance':assert len([e for e in events if e.get('Action')=='pass' and 'Test' in e])=={'root':21179,'services':219}[run['name']]
helper=p.parents[2]/'benchmarks/profiles/prehashed-relations-512/validation-controller/validate.py';assert sha(helper)==full['helperSha256']
spec=importlib.util.spec_from_file_location('conformance_readback',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
run=full['runs'][2]
with tempfile.TemporaryDirectory(prefix='direct-instantiation-readback-') as temporary:
 copy=dict(run)
 for stream in ['stdout','stderr']:
  raw=Path(run[stream]);target=Path(temporary)/raw.name;target.write_bytes(gzip.decompress(raw.with_suffix(raw.suffix+'.gz').read_bytes()));copy[stream]=str(target)
 summary=module.summarize_run(copy)
 assert not summary['integrity_errors'] and summary['source_configuration_cases']=={'total':14915,'fully_checked':12789,'partially_checked':8,'unsupported_skipped':2118,'failed':0}
cli=json.loads((p/'final-cli.json').read_text());assert cli['passed']
assert [r['mode'] for r in cli['runs']]==['normal','integration','race','checkptr']
for field,name in [('freezeSha256','cli-freeze.json'),('commonSha256','final_common.py'),('normalBuildSha256','build.json'),('controllerSha256','validate-cli.py')]:assert cli[field]==sha(p/name)
build=json.loads((p/'build.json').read_text());assert build['exitCode']==0 and build['sources']==sources
for file,digest in cli['comparators'].items():assert sha(file)==digest
for run in cli['runs']:
 assert run['passed'] and run['exitCode']==0
 if run['mode'] in ['race','checkptr']:
  flag='-race' if run['mode']=='race' else '-gcflags=all=-d=checkptr=2'
  binary=Path('/tmp/tsc-direct-instantiation-loops-validation/cli')/('tsc-go-'+run['mode'])
  assert run['buildExitCode']==0 and run['buildCommand']==['/tmp/tsc-toolchains/go/bin/go','build',flag,'-trimpath','-overlay',str(p/'overlay.json'),'-o',str(binary),'./cmd/tsgo']
  log=run['buildLog'];archive=p/'final-cli-logs'/log['file'];data=gzip.decompress(archive.read_bytes())
  assert sha(archive)==log['sha256'] and hashlib.sha256(data).hexdigest()==log['rawSha256']
 else:
  binary=Path(build['command'][build['command'].index('-o')+1]);assert run['binarySha256']==build['binarySha256']
 assert sha(binary)==run['binarySha256']
 count=12 if run['mode']=='integration' else 80
 assert run['counts']=={'tests':count,'pass':count,'fail':0,'cancelled':0,'skipped':0,'todo':0}
 log=run['log'];f=p/'final-cli-logs'/log['file'];data=gzip.decompress(f.read_bytes())
 assert sha(f)==log['sha256'] and hashlib.sha256(data).hexdigest()==log['rawSha256']
 text=re.sub(r'\x1b\[[0-9;]*m','',data.decode())
 assert {k:int(v) for k,v in re.findall(r'^(?:ℹ\s*)?(tests|pass|fail|cancelled|skipped|todo)\s+(\d+)\s*$',text,re.M)}==run['counts']
(p/'readback.json').write_text(json.dumps({'passed':True,'sources':sources,'evidence':{n:sha(p/n) for n in ['validation.json','baseline-validation.json','source-audit.json','full-validation.json','final-cli.json']},'verifierSha256':sha(__file__)},indent=2)+'\n')
print('Full raw-evidence readback passed')
