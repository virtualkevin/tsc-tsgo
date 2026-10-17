from pathlib import Path
import subprocess,json,os,hashlib,time,re,sys,traceback
R=Path('/home/dev/tssss/tsc-tsgo'); O=Path(sys.argv[1]); O.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
project=next(p for p in json.loads((R/'benchmarks/workloads.json').read_text())['projects'] if p['name']==sys.argv[2]); cwd=R/project['directory']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=cwd,text=True).strip()==project['commit']
binaries={'base':R/'packages/tsc-go/dist/tsc-go-keybuilder-saturated','observed':R/'packages/tsc-go/dist/tsc-go-semantic-families'}
assert sha(binaries['base'])=='2bdcca53f630535846054eada84cae8afaa32b4faab21de029eca41c79e26303'
assert sha(binaries['observed'])=='b919e1c0e13a644bc2dfad2dba114f14e072942b08becd7ccb73740288a9407a'
immutable={str(p):sha(p) for p in list(binaries.values())+[Path(str(p)+'.provenance.json') for p in binaries.values()]+[Path(__file__),R/'benchmarks/workloads.json',cwd/project['lockfile']]}
preflight=json.loads(Path('/tmp/tsc-census-families/workload-preflight.json').read_text());assert preflight['status']=='passed'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==preflight['head']
env={k:v for k,v in os.environ.items() if not k.startswith(('TSC_','TS_GO_')) and k not in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','CPUPROFILE','HEAPPROFILE','NODE_OPTIONS']};env['TSC_GO_CENSUS_MODE']='families';env['TSC_TS_LIB_DIR']=str(R/'upstream/typescript-go/internal/bundled/libs')
report={'status':'running','purpose':'diagnostic pilot; single samples are not optimization speedup evidence','project':project,'preflight':preflight,'immutable':immutable,'runs':[],'comparisons':[]}
def save(): (O/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
def call(binary,args,name,e):
 start=time.monotonic();r=subprocess.run([str(binary),*args],cwd=cwd,env=e,capture_output=True,text=True,timeout=300);elapsed=time.monotonic()-start
 (O/(name+'.stdout')).write_text(r.stdout);(O/(name+'.stderr')).write_text(r.stderr)
 item={'name':name,'command':[str(binary),*args],'cwd':str(cwd),'exit':r.returncode,'elapsedSeconds':elapsed,'stdoutSha256':sha(O/(name+'.stdout')),'stderrSha256':sha(O/(name+'.stderr'))};report['runs'].append(item);save();return r,item
semantic=['Files','Lines','Identifiers','Symbols','Types','Instantiations']
def split(r):
 # Profiling footer is emitted after ordinary compiler diagnostics/statistics.
 lines=[l for l in r.stdout.splitlines(True) if not l.startswith(('CPU profile: ','Memory profile: '))];out=''.join(lines)
 m=re.search(r'^Files:\s+\d+\s*$',out,re.M);assert m,(r.returncode,out[-1200:]);stats={l.split(':',1)[0]:l.split(':',1)[1].strip() for l in out[m.start():].splitlines()}
 return out[:m.start()],{k:int(stats[k]) for k in semantic}
try:
 for owners in [1,4]:
  args=['-p',project['project'],'--noEmit','--incremental','false','--composite','false','--noCheck','false','--pretty','false','--checkers',str(owners)]+project.get('args',[])
  a,_=call(binaries['base'],args+['--listFilesOnly'],f'{owners}-base-inputs',env)
  b,_=call(binaries['observed'],args+['--listFilesOnly'],f'{owners}-observed-inputs',env)
  assert a.returncode==b.returncode==0 and a.stdout==b.stdout and a.stderr==b.stderr==''
  inputs={str(Path(l) if Path(l).is_absolute() else cwd/l):sha(Path(l) if Path(l).is_absolute() else cwd/l) for l in a.stdout.splitlines()};assert len(inputs)>500
  (O/f'{owners}-inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
  control=None
  for variant in ['base','unlabeled','labeled']:
   name=f'{owners}-{variant}';profile=O/(name+'-profiles');e=dict(env);binary=binaries['base' if variant=='base' else 'observed']
   if variant!='base':e['TSC_GO_CENSUS']=str(O/(name+'.census.jsonl'));e['TSC_GO_CENSUS_CPU_LABELS']='1' if variant=='labeled' else '0'
   result,item=call(binary,args+['--extendedDiagnostics','--pprofDir',str(profile)],name,e);diagnostics,counters=split(result)
   assert result.stderr==''
   if variant=='base':control=(result.returncode,diagnostics,counters)
   else:
    assert (result.returncode,diagnostics,counters)==control,'compiler output changed'
    rows=[json.loads(l) for l in Path(e['TSC_GO_CENSUS']).read_text().splitlines()];header,*rows=rows
    assert header['semanticallyEquivalentResultsProven'] is False and len(rows)==owners
    assert all(row['cpuLabels']==(variant=='labeled') and row['familyOnly'] is True and len(row['records'])<=4 and row['overflow']['Calls']==0 for row in rows)
    item['census']={'sha256':sha(e['TSC_GO_CENSUS']),'records':sum(len(r['records']) for r in rows),'overflowCalls':sum(r['overflow']['Calls'] for r in rows),'calls':sum(sum(x['Calls'] for x in r['records'])+r['overflow']['Calls'] for r in rows),'owners':owners}
    report['comparisons'].append({'name':name,'status':'passed','counters':counters})
   item['profiles']={str(p):sha(p) for p in profile.iterdir()};assert len(item['profiles'])==2
   for path,h in inputs.items():assert sha(path)==h
   save();print(name,'passed',item.get('census',{}),flush=True)
 for path,h in immutable.items():assert sha(path)==h
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==preflight['head']
 report['status']='passed'
except BaseException as ex:report['status']='failed';report['error']=traceback.format_exc();raise
finally:save()
