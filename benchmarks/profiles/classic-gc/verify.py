from pathlib import Path
import gzip,hashlib,json,re,importlib.util,tempfile,subprocess,sys
sys.dont_write_bytecode=True
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
build=json.loads((p/'build.json').read_text());assert build['passed']
full=json.loads((p/'full-validation.json').read_text());assert full['passed'] and full['experiment']=='nogreenteagc'
assert full['buildReportSha256']==sha(p/'build.json')
assert full['controllerSha256']==sha(p/'validate-full.py')
assert [r['name'] for r in full['runs']]==['lifetime-normal','lifetime-race','lifetime-checkptr','root','services','conformance']
for run in full['runs']:
 assert run['passed'] and run['exit_code']==0
 for stream in ['stdout','stderr']:
  raw=Path(run[stream]);archive=raw.with_suffix(raw.suffix+'.gz');data=gzip.decompress(archive.read_bytes())
  assert sha(archive)==run['archive'][archive.name] and hashlib.sha256(data).hexdigest()==run[stream+'_sha256']
  if stream=='stdout':
   events=[json.loads(x) for x in data.splitlines()]
   assert not any(e.get('Action') in ['fail','build-fail'] for e in events)
   if run['name']!='conformance':assert len([e for e in events if e.get('Action')=='pass' and 'Test' in e])=={'lifetime-normal':9,'lifetime-race':9,'lifetime-checkptr':9,'root':21175,'services':219}[run['name']]
helper=p.parents[2]/'benchmarks/profiles/prehashed-relations-512/validation-controller/validate.py';assert sha(helper)==full['helperSha256']
spec=importlib.util.spec_from_file_location('conformance_readback',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
run=full['runs'][-1]
with tempfile.TemporaryDirectory(prefix='classic-gc-readback-') as temporary:
 copy=dict(run)
 for stream in ['stdout','stderr']:
  raw=Path(run[stream]);target=Path(temporary)/raw.name;target.write_bytes(gzip.decompress(raw.with_suffix(raw.suffix+'.gz').read_bytes()));copy[stream]=str(target)
 summary=module.summarize_run(copy)
 assert not summary['integrity_errors'] and summary['source_configuration_cases']=={'total':14915,'fully_checked':12789,'partially_checked':8,'unsupported_skipped':2118,'failed':0}
cli=json.loads((p/'final-cli.json').read_text());assert cli['passed']
assert [r['mode'] for r in cli['runs']]==['normal','integration','race','checkptr']
for field,name in [('fullValidationSha256','full-validation.json'),('commonSha256','final_common.py'),('normalBuildSha256','build.json'),('controllerSha256','validate-cli.py')]:assert cli[field]==sha(p/name)
build=json.loads((p/'build.json').read_text());assert build['exitCode']==0 and build['sourceSha256']=='216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd'
for file,digest in cli['comparators'].items():assert sha(file)==digest
for run in cli['runs']:
 assert run['passed'] and run['exitCode']==0
 if run['mode'] in ['race','checkptr']:
  flag='-race' if run['mode']=='race' else '-gcflags=all=-d=checkptr=2'
  binary=Path('/tmp/tsc-classic-gc-validation/cli')/('tsc-go-'+run['mode'])
  assert run['buildExitCode']==0 and run['buildCommand']==['/tmp/tsc-toolchains/go/bin/go','build',flag,'-trimpath','-o',str(binary),'./cmd/tsgo']
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
(p/'readback.json').write_text(json.dumps({'passed':True,'sourceSha256':build['sourceSha256'],'evidence':{n:sha(p/n) for n in ['build.json','full-validation.json','final-cli.json']},'verifierSha256':sha(__file__)},indent=2)+'\n')
print('Full raw-evidence readback passed')
