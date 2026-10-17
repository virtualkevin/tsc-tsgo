from pathlib import Path
import json,subprocess,os,re
R=Path('/home/dev/tssss/tsc-tsgo');D=Path('/tmp/tsc-worker-trace-typeorm-controls');D.mkdir()
original=json.loads(Path('/tmp/tsc-worker-trace-typeorm/report.json').read_text());baseline=original['runs'][0]
env={k:v for k,v in os.environ.items() if not k.startswith(('TSC_','TS_GO_','SCRIPTC_','GODEBUG_')) and k not in ['GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOEXPERIMENT','NODE_OPTIONS','LD_PRELOAD','CPUPROFILE','HEAPPROFILE']};env['TSC_TS_LIB_DIR']=str(R/'upstream/typescript-go/internal/bundled/libs')
rows=[]
for i in range(6):
 p=subprocess.run(baseline['command'],cwd=R/'upstream/benchmarks/typeorm',env=env,capture_output=True,text=True,timeout=120)
 (D/f'{i}.stdout').write_text(p.stdout);(D/f'{i}.stderr').write_text(p.stderr)
 assert p.returncode==0 and not p.stderr
 counters={k:int(v) for k,v in re.findall(r'^(Files|Lines|Identifiers|Symbols|Types|Instantiations):\s*(\d+)\s*$',p.stdout,re.M)}
 assert len(counters)==6
 rows.append({'run':i,'counters':counters,'differences':{k:[baseline['counters'][k],v] for k,v in counters.items() if baseline['counters'][k]!=v}})
 (D/'report.json').write_text(json.dumps({'status':'running' if i<5 else 'complete','command':baseline['command'],'rows':rows},indent=2)+'\n')
print(json.dumps(rows))
