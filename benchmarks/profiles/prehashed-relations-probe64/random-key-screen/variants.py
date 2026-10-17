from pathlib import Path
import hashlib,json,os,subprocess,difflib
root=Path('/tmp/tsc-prehashed-relation-random-screen');env=os.environ.copy()
for name in ['GOFLAGS','GOWORK','GOGC','GOMEMLIMIT','GODEBUG']:env.pop(name,None)
env['GOMAXPROCS']='1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for limit in [128,256]:
 p=root/f'probe-{limit}';p.mkdir(exist_ok=False)
 original=(root/'relation_results.go').read_text();updated=original.replace('const relationResultProbeLimit = 64',f'const relationResultProbeLimit = {limit}');assert updated!=original
 (p/'relation_results.go').write_text(updated)
 for file in ['main.go','go.mod']:(p/file).write_bytes((root/file).read_bytes())
 (p/'parameter.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),updated.splitlines(True),fromfile='probe-64/relation_results.go',tofile=f'probe-{limit}/relation_results.go')))
 commands=[]
 for argv,output in [(['/tmp/tsc-toolchains/go/bin/go','build','-o','screen','.'],'build'),(['./screen'],'results')]:
  with (p/(output+'.stdout')).open('wb') as out,(p/(output+'.stderr')).open('wb') as err:
   result=subprocess.run(argv,cwd=p,env=env,stdout=out,stderr=err,timeout=180)
  commands.append({'argv':argv,'cwd':str(p),'stdout':output+'.stdout','stderr':output+'.stderr','exitCode':result.returncode})
  assert result.returncode==0,commands
 rows=[json.loads(l) for l in (p/'results.stdout').read_text().splitlines()];assert len(rows)==10
 summary={'scope':'Synthetic parameter screening; no compiler workload/correctness validation or time/memory claim','probeLimit':limit,'loadThreshold':0.75,'baselineSourceSha256':sha(root/'relation_results.go'),'variantSourceSha256':sha(p/'relation_results.go'),'driverSha256':sha(p/'main.go'),'parameterPatchSha256':sha(p/'parameter.patch'),'binarySha256':sha(p/'screen'),'commands':commands,'environment':{'unset':['GOFLAGS','GOWORK','GOGC','GOMEMLIMIT','GODEBUG'],'GOMAXPROCS':'1'},'rows':rows,'fallbacks':sum(r['fallback'] for r in rows),'allProcessesTerminal':True}
 (p/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps({'probeLimit':limit,'fallbacks':summary['fallbacks'],'inserts':[r.get('attemptedInsert',r.get('finalCount')) for r in rows]}),flush=True)
