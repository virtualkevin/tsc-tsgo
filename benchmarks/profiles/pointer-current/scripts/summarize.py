import datetime,hashlib,json,os,pathlib,signal,subprocess,sys,time
D=pathlib.Path('/tmp/tsc-pointer-current-profiles');GO=pathlib.Path('/tmp/tsc-toolchains/go/bin/go');CAPTURE=D/'capture.json';REPORT=D/'summary-evidence.json'
if REPORT.exists():raise SystemExit('Refusing to overwrite existing summary evidence')
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
c=json.loads(CAPTURE.read_text());assert c['status']=='passed'
binary=pathlib.Path(c['binary']);sidecar=pathlib.Path(str(binary)+'.provenance.json')
assert c['binarySha256']=='b1a592d593d3415603062016bfd35b11b810f31f9a49b008ec2292e661a15322'
assert c['sourceSha256']=='6beaa7324ec7dbf09a8b2776bda64b6d5b0d2e93ead3b27ccc4d3aabf5c43d3d'
assert sha(binary)==c['binarySha256'] and sha(sidecar)==c['sidecarSha256']
assert set(r['name'] for r in c['runs'])=={'typeorm','trpc','vscode','sentry'}
raw={str(CAPTURE):sha(CAPTURE),str(binary):sha(binary),str(sidecar):sha(sidecar),str(GO):sha(GO)}
for r in c['runs']:
 assert r['status']=='passed'
 for p in r['profiles'].values():assert sha(p['path'])==p['sha256'];raw[p['path']]=p['sha256']
report={'schemaVersion':1,'status':'running','startedAt':now(),'purpose':'Decode validated CPU/allocation profiles into bounded text summaries. This is not performance timing.','capture':str(CAPTURE),'captureSha256':raw[str(CAPTURE)],'binary':str(binary),'binarySha256':c['binarySha256'],'sourceSha256':c['sourceSha256'],'sidecarSha256':c['sidecarSha256'],'goExecutable':str(GO),'goExecutableSha256':raw[str(GO)],'rawBefore':raw,'commands':[],'projects':[]}
active=None;cancelled=None;deadline=time.monotonic()+900
def save():
 temp=D/'summary-evidence.pending.json';temp.write_text(json.dumps(report,indent=2)+'\n');temp.replace(REPORT)
def kill():
 if active is not None:
  try:os.killpg(active.pid,signal.SIGKILL)
  except ProcessLookupError:pass
def handler(s,f):
 global cancelled
 cancelled=signal.Signals(s).name;kill()
signal.signal(signal.SIGINT,handler);signal.signal(signal.SIGTERM,handler)
env=os.environ.copy()
for k in ['GOFLAGS','GOWORK','GOCOVERDIR','GODEBUG','GOGC','GOMEMLIMIT','GOMAXPROCS','PPROF_BINARY_PATH','PPROF_TMPDIR','PPROF_TOOLS','LLVM_PROFILE_FILE']:env.pop(k,None)
env.update({'GOTOOLCHAIN':'local','GOENV':'off'})
report['toolEnvironmentOverrides']={'GOTOOLCHAIN':'local','GOENV':'off'}
def run(args,stdout,stderr):
 global active
 assert not cancelled and time.monotonic()<deadline
 command=[str(GO),*args];item={'command':command,'cwd':str(D),'stdout':str(stdout),'stderr':str(stderr)};report['commands'].append(item);save()
 try:
  with stdout.open('xb') as out,stderr.open('xb') as err:
   active=subprocess.Popen(command,cwd=D,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True)
   active.wait(timeout=min(120,max(.1,deadline-time.monotonic())))
   item['exitCode']=active.returncode
  item['stdoutSha256']=sha(stdout);item['stderrSha256']=sha(stderr)
  assert not cancelled and active.returncode==0, 'pprof/version command failed'
  assert stdout.stat().st_size>0 and stdout.stat().st_size<8*1024*1024,'Unexpected output size'
  assert stderr.read_text()=='','Unexpected tool diagnostics'
  save();return item
 finally:
  kill()
  if active is not None:active.wait(timeout=10)
  active=None
try:
 version=run(['version'],D/'go-version.txt',D/'go-version.stderr.txt');report['goVersion']=(D/'go-version.txt').read_text().strip();assert 'go1.26.9' in report['goVersion']
 definitions=[('cpu-flat','CPU','cpu',False),('cpu-cum','CPU','cpu',True),('alloc-space-flat','Memory','alloc_space',False),('alloc-space-cum','Memory','alloc_space',True),('alloc-objects-flat','Memory','alloc_objects',False)]
 for r in c['runs']:
  directory=D/r['name'];project={'name':r['name'],'summaries':[]};report['projects'].append(project)
  for label,kind,index,cum in definitions:
   profile=r['profiles'][kind];assert sha(profile['path'])==profile['sha256'] and sha(binary)==c['binarySha256']
   args=['tool','pprof','-top','-nodecount=300','-nodefraction=0','-edgefraction=0','-sample_index='+index]
   if cum:args.append('-cum')
   args += [str(binary),profile['path']]
   item=run(args,directory/(label+'.txt'),directory/(label+'.stderr.txt'))
   text=(directory/(label+'.txt')).read_text();assert 'Showing nodes accounting for' in text and 'flat' in text and 'cum' in text,'Profile did not decode to expected table'
   project['summaries'].append({'kind':kind,'sampleIndex':index,'order':'cumulative' if cum else 'flat','nodeCountLimit':300,**item})
  save();print('Summaries ready:',r['name'],flush=True)
 report['rawAfter']={p:sha(p) for p in raw};assert report['rawAfter']==raw
 report['status']='passed';report['profilesDecoded']=sum(len(r['profiles']) for r in c['runs']);report['summaryCount']=sum(len(p['summaries']) for p in report['projects']);assert report['profilesDecoded']==8 and report['summaryCount']==20
except BaseException as e:
 report['status']='failed';report['error']=type(e).__name__+': '+str(e);print(report['error'],file=sys.stderr)
finally:
 kill();report['finishedAt']=now();report['limitations']=['Sampled CPU fractions overlap between callers/callees and are not additive wall-time speedup predictions.','alloc_space and alloc_objects are cumulative sampled allocation estimates, not live heap or peak RSS.','Tables retain up to300 nodes with node/edge filtering disabled; raw profiles remain authoritative.','Profile capture was unwrapped and instrumented; these outputs are not comparable with benchmark wall-time medians.'];save()
sys.exit(0 if report['status']=='passed' else 1)
