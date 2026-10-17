from pathlib import Path
import hashlib,json,os,re,subprocess
R=Path('/home/dev/tssss/tsc-tsgo');D=Path('/tmp/tsc-worker-trace-smoke');D.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
B=R/'packages/tsc-go/dist/tsc-go-node-pointer';C=R/'packages/tsc-go/dist/tsc-go-worker-trace'
E={k:v for k,v in os.environ.items() if not k.startswith(('TSC_','TS_GO_','SCRIPTC_','GODEBUG_')) and k not in ['GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOEXPERIMENT','NODE_OPTIONS','LD_PRELOAD','CPUPROFILE','HEAPPROFILE']}
E['TSC_TS_LIB_DIR']=str(R/'upstream/typescript-go/internal/bundled/libs')
P=next(x for x in json.loads((R/'benchmarks/workloads.json').read_text())['projects'] if x['name']=='trpc')
report={'status':'running','binaries':{str(p):sha(p) for p in [B,C]},'runs':[],'scope':'Diagnostic smoke only; not performance evidence'}
def save(): (D/'report.json').write_text(json.dumps(report,indent=2)+'\n')
save()
try:
 for n in [1,4]:
  control=None
  for name,bin in [('baseline',B),('disabled',C),('enabled',C)]:
   label=f'{n}-{name}';env=dict(E);trace=D/f'{label}.trace'
   if name=='enabled':env['TSC_GO_EXEC_TRACE']=str(trace)
   cmd=[str(bin),'-p',P['project'],'--noEmit','--incremental','false','--composite','false','--noCheck','false','--pretty','false','--checkers',str(n),'--extendedDiagnostics']
   proc=subprocess.run(cmd,cwd=R/P['directory'],env=env,capture_output=True,text=True,timeout=120)
   (D/f'{label}.stdout').write_text(proc.stdout);(D/f'{label}.stderr').write_text(proc.stderr)
   counters={k:int(v) for k,v in re.findall(r'^(Files|Lines|Identifiers|Symbols|Types|Instantiations):\s*(\d+)\s*$',proc.stdout,re.M)}
   assert len(counters)==6 and proc.returncode==0 and not proc.stderr,(label,proc.returncode,proc.stderr)
   assert not re.search(r'error TS\d+',proc.stdout),label
   if control is None:control=counters
   assert counters==control,(label,counters,control)
   item={'label':label,'command':cmd,'returncode':proc.returncode,'counters':counters,'stdoutSha256':sha(D/f'{label}.stdout')}
   if name=='enabled':
    parsed=D/f'{label}.parsed.txt'
    with parsed.open('w') as f:
     decode=subprocess.run(['/tmp/tsc-toolchains/go/bin/go','tool','trace','-d=parsed',str(trace)],stdout=f,stderr=subprocess.PIPE,text=True,timeout=60)
    (D/f'{label}.decode.stderr').write_text(decode.stderr)
    assert decode.returncode==0,decode.stderr
    subprocess.run(['python3','/tmp/tsc-worker-trace-draft/analyze.py',str(parsed),str(D/f'{label}.analysis.json')],check=True,timeout=60)
    item['traceSha256']=sha(trace);item['analysis']=json.loads((D/f'{label}.analysis.json').read_text())
   report['runs'].append(item);save()
 report['status']='passed'
except BaseException as e:
 report['status']='failed';report['error']=repr(e);raise
finally:save()
print(json.dumps({'status':report['status'],'runs':len(report['runs'])}))
