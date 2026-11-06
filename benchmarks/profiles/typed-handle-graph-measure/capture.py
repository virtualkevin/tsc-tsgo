from pathlib import Path
import hashlib,json,os,re,signal,subprocess,time
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
v=json.loads((p/'validation.json').read_text());assert v['status']=='passed'
assert all(x['ok'] and x['exitCode']==0 and len(x['passed'])==7 for x in v['runs'])
cfg=json.loads((p/'config.json').read_text());binary=Path(v['build']['binary']);assert sha(binary)==v['build']['binarySha256']
assert all(sha(k)==h for k,h in v['sources'].items())
env=os.environ.copy();removed=[]
for key in list(env):
 if key.startswith(('GRAPH_PROBE_','TSC_','TS_GO_','SCRIPTC_')) or key in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','GOOS','GOARCH','GOAMD64','GOCOVERDIR','LD_PRELOAD','MALLOC_CONF','MALLOC_ARENA_MAX']:
  removed.append(key);env.pop(key,None)
raw=p/'raw';raw.mkdir(exist_ok=False)
report={'status':'running','scope':cfg['scope'],'configSha256':sha(p/'config.json'),'validationSha256':sha(p/'validation.json'),'controllerSha256':sha(__file__),'binarySha256':sha(binary),'sources':v['sources'],'removedEnvironmentNames':sorted(removed),'observations':[]}
output=p/'capture.json';assert not output.exists()
def save():output.write_text(json.dumps(report,indent=2)+'\n')
child=None
def cleanup():
 if child is not None and child.poll() is None:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
def cancel(sig,frame):cleanup();raise SystemExit(128+sig)
for sig in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]:signal.signal(sig,cancel)
def run(kind,case,n,pair,side):
 global child
 label=f'{kind}-{case}-n{n}-pair{pair}-{side}';out=raw/(label+'.stdout');err=raw/(label+'.stderr')
 if kind=='benchmark':
  pattern=f'^BenchmarkStorage$/^{case}$/^{side}$/^n{n}$'
  command=[str(binary),'-test.run=^$','-test.bench='+pattern,'-test.benchtime='+cfg['benchtime'],'-test.benchmem','-test.count=1'];runenv=env
 else:
  command=[str(binary),'-test.run=^TestStorageRetentionProbe$','-test.v','-test.count=1'];runenv=env|{'GRAPH_PROBE_SIDE':side,'GRAPH_PROBE_N':str(n),'GRAPH_PROBE_SHAPE':case}
 with out.open('xb') as a,err.open('xb') as b:
  child=subprocess.Popen(command,env=runenv,cwd=p,stdout=a,stderr=b,start_new_session=True)
  try:code=child.wait(timeout=120)
  finally:cleanup();child=None
 assert code==0 and err.read_bytes()==b'',(label,code)
 text=out.read_text();row={'kind':kind,'case':case,'n':n,'pair':pair,'side':side,'command':command,'exitCode':code,'stdout':out.name,'stderr':err.name,'stdoutSha256':sha(out),'stderrSha256':sha(err)}
 if kind=='benchmark':
  pattern=rf'^BenchmarkStorage/{case}/{side}/n{n}(?:-(\d+))?\s+(\d+)\s+([0-9.e+]+) ns/op\s+(\d+) B/op\s+(\d+) allocs/op\s*$'
  matches=re.findall(pattern,text,re.M);assert len(matches)==1,(label,text)
  cpus,iterations,ns,allocated,allocs=matches[0]
  row.update(cpus=int(cpus or 1),iterations=int(iterations),nsPerOp=float(ns),bytesPerOp=int(allocated),allocsPerOp=int(allocs));assert row['iterations']>0 and row['nsPerOp']>0
 else:
  lines=[line.split('RETENTION ',1)[1] for line in text.splitlines() if 'RETENTION ' in line];assert len(lines)==1
  data=json.loads(lines[0]);assert data['side']==side and data['shape']==case and data['records']==n and data['rootPayload']==n*0x100000001
  assert data['after']['NumGC']>=data['before']['NumGC']+2
  assert data['heapAllocDelta']==data['after']['HeapAlloc']-data['before']['HeapAlloc']
  assert data['totalAllocDelta']==data['after']['TotalAlloc']-data['before']['TotalAlloc']
  assert data['compactAllocatedSlots']==(n if side=='compact' else 0)
  row['retention']=data
 report['observations'].append(row);save()
save()
try:
 for kind,cases,pairs in [('benchmark',cfg['operations'],cfg['benchmarkPairs']),('retention',cfg['shapes'],cfg['retentionPairs'])]:
  for n in cfg['sizes']:
   for case in cases:
    for pair in range(pairs):
     sides=cfg['sides'] if pair%2==0 else list(reversed(cfg['sides']))
     for side in sides:run(kind,case,n,pair,side)
    print(kind,case,n,'complete',flush=True)
 assert sha(binary)==report['binarySha256'] and all(sha(k)==h for k,h in report['sources'].items())
 assert sha(__file__)==report['controllerSha256'] and sha(p/'config.json')==report['configSha256']
 report['status']='passed'
except BaseException as e:report['status']='failed';report['error']=repr(e);raise
finally:cleanup();save()
