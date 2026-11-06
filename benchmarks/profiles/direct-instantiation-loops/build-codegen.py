from pathlib import Path
import os,hashlib,json,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOOS','GOARCH','GOAMD64','GORACE']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
report={'status':'running','controllerSha256':sha(__file__),'runs':[]};output=p/'codegen.json';assert not output.exists()
try:
 for prefix in ['', 'baseline-']:
  overlay=p/(prefix+'overlay.json');sources=json.loads(overlay.read_text())['Replace'];frozen={k:sha(v) for k,v in sources.items()};binary='/tmp/direct-instantiation-'+(prefix or 'candidate-')+'test'
  cmd=['/tmp/tsc-toolchains/go/bin/go','test','-c','-overlay',str(overlay),'-o',binary,'./internal/checker']
  with (p/(prefix+'build.stdout')).open('x') as out,(p/(prefix+'build.stderr')).open('x') as err:code=subprocess.run(cmd,cwd=r/'packages/tsc-go',env=env,stdout=out,stderr=err).returncode
  assert code==0
  command=['/tmp/tsc-fused-objdump/objdump','-s',r'checker\.\(\*Checker\)\.instantiate(Types|Symbols|Signatures|IndexInfos)$|checker\.instantiateList',binary]
  raw=subprocess.check_output(command);(p/(prefix+'assembly.txt')).write_bytes(raw)
  assert frozen=={k:sha(v) for k,v in sources.items()}
  report['runs'].append({'prefix':prefix,'command':cmd,'exitCode':code,'binary':binary,'binarySha256':sha(binary),'sources':frozen,'toolchainSha256':sha(cmd[0]),'objdumpCommand':command,'objdumpSha256':sha(command[0]),'assemblySha256':hashlib.sha256(raw).hexdigest()})
  output.write_text(json.dumps(report,indent=2)+'\n');print(prefix+'codegen captured',flush=True)
 report['status']='passed'
except BaseException as e:report['status']='failed';report['error']=repr(e);raise
finally:output.write_text(json.dumps(report,indent=2)+'\n')
