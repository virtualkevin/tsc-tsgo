from pathlib import Path
import json,subprocess,os,re,hashlib
R=Path('/home/dev/tssss/tsc-tsgo');D=Path('/tmp/tsc-census-families/typeorm-symbol-audit');D.mkdir()
source=json.loads(Path('/tmp/tsc-census-families/typeorm/summary.json').read_text());original=next(x for x in source['runs'] if x['name']=='4-base')
env={k:v for k,v in os.environ.items() if not k.startswith(('TSC_','TS_GO_')) and k not in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','CPUPROFILE','HEAPPROFILE','NODE_OPTIONS']};env['TSC_TS_LIB_DIR']=str(R/'upstream/typescript-go/internal/bundled/libs')
report={'status':'running','purpose':'baseline-only counter stability audit; does not rescue failed comparison','runs':[],'sourceSummarySha256':hashlib.sha256(Path('/tmp/tsc-census-families/typeorm/summary.json').read_bytes()).hexdigest()}
try:
 for i in range(6):
  args=list(original['command']);args[-1]=str(D/f'{i}-profiles')
  r=subprocess.run(args,cwd=original['cwd'],env=env,capture_output=True,text=True,timeout=300)
  (D/f'{i}.stdout').write_text(r.stdout);(D/f'{i}.stderr').write_text(r.stderr)
  out=''.join(l for l in r.stdout.splitlines(True) if not l.startswith(('CPU profile: ','Memory profile: ')));m=re.search(r'^Files:\s+\d+\s*$',out,re.M);assert m
  stats={l.split(':',1)[0]:l.split(':',1)[1].strip() for l in out[m.start():].splitlines()}
  counters={k:int(stats[k]) for k in ['Files','Lines','Identifiers','Symbols','Types','Instantiations']}
  assert r.returncode==0 and r.stderr=='' and out[:m.start()]==''
  report['runs'].append({'command':args,'exit':r.returncode,'counters':counters});(D/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(i,counters,flush=True)
 report['status']='passed'
finally:(D/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
