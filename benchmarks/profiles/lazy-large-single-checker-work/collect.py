import datetime,hashlib,json,os,pathlib,re,subprocess
root=pathlib.Path(__file__).resolve().parents[3]
def parse_native_trace(stderr):
    # Refuse parallel records: retired/replacement workers can reuse an index.
    if re.search(r'^checkers: thread \d+ checked ', stderr, re.M):
        raise ValueError('Parallel checker records are not a single-checker sample')
    lines = [line for line in stderr.splitlines() if line.startswith('checkers: single ')]
    if len(lines) != 1:
        raise ValueError(f'Expected exactly one single-checker trace, found {len(lines)}')
    match = re.fullmatch(
        r'checkers: single types (\d+) inst (\d+) user \d+ sys \d+ '
        r'rss \S+MB symlinks (\d+) nodelinks (\d+) sigs (\d+) rel (\d+)', lines[0])
    if match is None:
        raise ValueError('Unrecognized single-checker trace format')
    names = ['Types', 'Instantiations', 'SymbolLinkEntries', 'NodeLinkEntries', 'Signatures', 'RelationEntries']
    return dict(zip(names, map(int, match.groups())))

def parse_extended(stdout):
    return {m.group(1): int(m.group(2).replace(',', '')) for m in re.finditer(
        r'^([A-Za-z][A-Za-z /()-]*?):\s+([\d,]+)\s*$', stdout, re.M)}
source=json.loads((root/'benchmarks/results/lazy-default-large.json').read_text())
controls=['GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','TSC_GO_SCHEDULER','TSC_GO_SHARED_GLOBALS','TSC_TS_CHECKERS','TSC_TS_REGION','TSC_TS_RECYCLE','TSC_TS_SIDE_STATE','TSC_TS_CHECKERS_TRACE']
env=os.environ.copy()
for key in controls:env.pop(key,None)
env['TSC_TS_LIB_DIR']=str(root/'upstream/typescript-go/internal/bundled/libs');env['TSC_TS_CHECKERS_TRACE']='1'
out=pathlib.Path('/tmp/tsc-lazy-large-work');out.mkdir(exist_ok=True)
report={'schemaVersion':1,'purpose':'Untimed single-checker work counters; concurrent builds may run. No timing/speedup claim.','benchmarkEvidence':'benchmarks/results/lazy-default-large.json','startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'unsetEnvironment':controls,'environmentOverrides':{k:env[k] for k in ['TSC_TS_LIB_DIR','TSC_TS_CHECKERS_TRACE']},'definitions':{'Types':'Created Type objects including initialization, one checker per process.','Instantiations':'Calls to instantiateTypeWorker after active mapper cache miss; not all checker work.'},'binaries':{k:{'path':b['path'],'sha256':b['sha256']}for k,b in source['binaries'].items()},'candidateSourceSha256':'39b165a093813ad622f9b276a3a9d6c433d0d6a91199ee6c897f3d8e3ed03a59','status':'running','projects':[]}
def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save():(out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
def verify(p):
 cwd=pathlib.Path(p['cwd'])
 if subprocess.check_output(['git','rev-parse','HEAD'],cwd=cwd,text=True).strip()!=p['commit']:raise ValueError('revision changed')
 if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=cwd,text=True).strip():raise ValueError('tracked changes')
 for entry in p['preflight']['candidate']['inputs']:
  if digest(cwd/entry['file'])!=entry['sha256']:raise ValueError('input changed: '+entry['file'])
 for b in report['binaries'].values():
  if digest(b['path'])!=b['sha256']:raise ValueError('binary changed')
save()
try:
 for name in ['sentry','vscode']:
  p=next(p for p in source['projects'] if p['name']==name);verify(p)
  record={k:p[k]for k in ['name','commit','cwd','scope','configSha256','lockfileSha256']};record.update({'inputCount':p['preflight']['candidate']['fileCount'],'inputFileListSha256':p['preflight']['candidate']['fileListSha256'],'runs':{},'status':'running'});report['projects'].append(record);save()
  for key,binary in report['binaries'].items():
   args=p['compilerArgs'][key]+['--checkers','1','--extendedDiagnostics']
   print('START',name,key,flush=True)
   run=subprocess.run([binary['path'],*args],cwd=p['cwd'],env=env,capture_output=True,text=True,timeout=600)
   stdout=out/(name+'-'+key+'.stdout.log');stderr=out/(name+'-'+key+'.stderr.log');stdout.write_text(run.stdout);stderr.write_text(run.stderr)
   result={'args':args,'exitCode':run.returncode,'stdout':stdout.name,'stderr':stderr.name,'stdoutSha256':digest(stdout),'stderrSha256':digest(stderr),'extendedCounters':parse_extended(run.stdout)};record['runs'][key]=result;save()
   if run.returncode or re.search(r'error TS\d+:',run.stdout+run.stderr):raise ValueError(name+' '+key+' failed')
   result['workCounters']=parse_native_trace(run.stderr)if key=='baseline'else{k:result['extendedCounters'][k]for k in ['Types','Instantiations']}
   if key=='baseline'and result['workCounters']['Types']!=result['extendedCounters']['Types']:raise ValueError('trace/extended Types differ')
   save();print('DONE',name,key,result['workCounters'],flush=True)
  a,b=record['runs']['baseline'],record['runs']['candidate']
  for key in ['Files','Lines','Identifiers']:
   if a['extendedCounters'][key]!=b['extendedCounters'][key]:raise ValueError('input counter mismatch '+key)
  record['comparison']={key:{'native':a['workCounters'][key],'go':b['workCounters'][key],'difference':b['workCounters'][key]-a['workCounters'][key],'goOverNative':b['workCounters'][key]/a['workCounters'][key]}for key in ['Types','Instantiations']}
  verify(p);record['status']='complete';save()
 report['status']='complete'
except BaseException as error:
 report['status']='failed';report['error']=str(error);raise
finally:
 report['finishedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
