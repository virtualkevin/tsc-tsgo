from pathlib import Path
import gzip,hashlib,json,re,subprocess,sys
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
subprocess.run([sys.executable,'-B',str(p/'verify-focused.py')],check=True)
subprocess.run([sys.executable,'-B',str(p/'source-audit.py')],check=True)
r=json.loads((p/'final-cli.json').read_text());assert r['passed']
for key,file in [('freezeSha256','cli-freeze.json'),('controllerSha256','validate-cli.py'),('commonSha256','final_common.py'),('normalBuildSha256','build.json')]:assert r[key]==sha(p/file)
for f,h in r['comparators'].items():assert sha(f)==h
freeze=json.loads((p/'cli-freeze.json').read_text());assert freeze['sources']=={k:sha(v) for k,v in json.loads((p/'overlay.json').read_text())['Replace'].items()}
build=json.loads((p/'build.json').read_text());assert build['exitCode']==0 and build['sources']==freeze['sources']
normal=Path('/tmp/tsc-reduction-scratch-candidate-validation/tsc-reduction-scratch-candidate');assert sha(normal)==build['binarySha256']
def check_flags(command,mode):
 flags=[x for x in command if x.startswith('-gcflags=')]
 expected=['-gcflags=github.com/microsoft/typescript-go/...=-l=4']
 if mode=='checkptr':expected=['-gcflags=all=-d=checkptr=2','-gcflags=github.com/microsoft/typescript-go/...=-l=4 -d=checkptr=2']
 assert flags==expected and ('-race' in command)==(mode=='race') and '-trimpath' in command
 assert command[command.index('-overlay')+1]==str(p/'overlay.json')
def read_archive(entry):
 f=p/'final-cli-logs'/entry['file'];assert sha(f)==entry['sha256']
 data=gzip.decompress(f.read_bytes());assert hashlib.sha256(data).hexdigest()==entry['rawSha256'];return data.decode()
check_flags(build['command'],'normal')
assert [x['mode'] for x in r['runs']]==['normal','integration','race','checkptr']
for run in r['runs']:
 mode=run['mode'];assert run['passed'] and run['exitCode']==0
 text=re.sub(r'\x1b\[[0-9;]*m','',read_archive(run['log']))
 counts={k:int(v) for k,v in re.findall(r'^(?:ℹ\s*)?(tests|pass|fail|cancelled|skipped|todo)\s+(\d+)\s*$',text,re.M)}
 expected=12 if mode=='integration' else 80
 assert counts==run['counts']=={'tests':expected,'pass':expected,'fail':0,'cancelled':0,'skipped':0,'todo':0}
 binary=normal
 if mode in ['race','checkptr']:
  check_flags(run['buildCommand'],mode);assert run['buildExitCode']==0;read_archive(run['buildLog'])
  binary=normal.parent/'cli'/('tsc-go-'+mode)
 assert sha(binary)==run['binarySha256']
(p/'cli-readback.json').write_text(json.dumps({'passed':True,'reportSha256':sha(p/'final-cli.json'),'verifierSha256':sha(__file__),'scope':'Archived CLI/API test counts, exact mode flags, comparator and binary hashes, frozen source hashes.'},indent=2)+'\n')
print('CLI/API raw readback passed')
