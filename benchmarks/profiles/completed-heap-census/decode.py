from pathlib import Path
import subprocess,json,hashlib,os
p=Path(__file__).resolve().parent;r=p.parents[2];sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
report=json.loads((p/'report.json').read_text());assert report['status']=='passed'
binary=Path('/tmp/tsc-completed-heap-census');assert sha(binary)==report['candidateSha256']
go='/tmp/tsc-toolchains/go/bin/go';out={'status':'running','goSha256':sha(go),'candidateSha256':sha(binary),'captureReportSha256':sha(p/'report.json'),'profiles':[]}
assert not (p/'decoded.json').exists()
env=os.environ.copy();env['GOTOOLCHAIN']='local'
for name in ['typeorm','trpc','vscode','sentry']:
 run=next(x for x in report['runs'] if x['project']==name and x['mode']=='enabled')
 for phase in ['before','after']:
  source=p/name/'heap'/(phase+'.pb.gz');assert sha(source)==run['artifacts'][source.name]['sha256']
  target=source.with_name(phase+'.raw.txt');error=source.with_name(phase+'.decode.stderr');assert not target.exists()
  cmd=[go,'tool','pprof','-raw',str(binary),str(source)]
  with target.open('w') as a,error.open('w') as b:code=subprocess.run(cmd,env=env,stdout=a,stderr=b,timeout=120).returncode
  assert code==0 and error.read_bytes()==b''
  out['profiles'].append({'project':name,'phase':phase,'command':cmd,'sourceSha256':sha(source),'rawSha256':sha(target),'stderrSha256':sha(error)})
out['status']='passed';(p/'decoded.json').write_text(json.dumps(out,indent=2)+'\n')
