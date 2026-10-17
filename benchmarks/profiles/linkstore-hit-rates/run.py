import json,pathlib,subprocess,os,hashlib,datetime,collections
root=pathlib.Path('/home/dev/tssss/tsc-tsgo');copy=pathlib.Path('/tmp/tsc-linkstore-run');binary=copy/'tsc-go-instrumented'
reports=[json.loads((root/f'benchmarks/results/{f}.json').read_text())for f in ['lazy-default','lazy-default-large']];projects={p['name']:p for r in reports for p in r['projects']};env=os.environ.copy()
for k in reports[0]['environment']['unsetEnvironment']:env.pop(k,None)
env.update(reports[0]['environment']['compilerEnvironment'])
files=[{'path':str(f.relative_to(copy)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in sorted((copy/'packages/tsc-go').rglob('*'))if f.is_file()];manifest=copy/'source-manifest.json';manifest.write_text(json.dumps(files,separators=(',',':'))+'\n')
out={'purpose':'Exploratory LinkStore last-inserted hit-rate counts; instrumentation overhead makes runtime unsuitable for performance comparisons.','baseCommit':'87b892e455d96083a6b4dcba48682189e679d3c3','patch':'/tmp/tsc-linkstore-instrumentation.patch','patchSha256':hashlib.sha256(pathlib.Path('/tmp/tsc-linkstore-instrumentation.patch').read_bytes()).hexdigest(),'sourceCopy':str(copy),'sourceManifest':str(manifest),'sourceManifestSha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'binary':str(binary),'binarySha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'buildCommand':['/tmp/tsc-toolchains/go/bin/go','build','-trimpath','-o',str(binary),'./cmd/tsgo'],'buildCwd':str(copy/'packages/tsc-go'),'buildEnvironment':{'GOGC':'100'},'buildMetadata':subprocess.check_output(['/tmp/tsc-toolchains/go/bin/go','version','-m',str(binary)],text=True),'compilerEnvironment':reports[0]['environment']['compilerEnvironment'],'unsetEnvironment':reports[0]['environment']['unsetEnvironment'],'timeoutSeconds':300,'runs':[]}
for name in ['trpc','sentry']:
 p=projects[name];prefix=copy/('counts-'+name);runenv={**env,'TSC_GO_LINKSTORE_PROFILE':str(prefix)};args=[str(binary),*p['compilerArgs']['candidate']];print('START',name,flush=True)
 try:r=subprocess.run(args,cwd=p['cwd'],env=runenv,capture_output=True,timeout=300);code=r.returncode;stdout=r.stdout;stderr=r.stderr
 except subprocess.TimeoutExpired as e:code='timeout';stdout=e.stdout or b'';stderr=e.stderr or b''
 (copy/(name+'-stdout.log')).write_bytes(stdout);(copy/(name+'-stderr.log')).write_bytes(stderr)
 paths=sorted(copy.glob('counts-'+name+'.*.json'));aggregate={};storecount=0
 for path in paths:
  profile=json.loads(path.read_text())
  for s in profile['stores']:
   storecount+=1
   assert s['lastInsertedMatches']<=s['mapHits']<=s['getCalls'],s
   assert s['insertions']==s['newCalls']+s['getCalls']-s['mapHits'],s
   key=s['keyType']+' -> '+s['valueType'];a=aggregate.setdefault(key,dict(stores=0,getCalls=0,lastInsertedMatches=0,mapHits=0,newCalls=0,insertions=0));a['stores']+=1
   for k in ['getCalls','lastInsertedMatches','mapHits','newCalls','insertions']:a[k]+=s[k]
 for a in aggregate.values():a['predictedGetHitRate']=a['lastInsertedMatches']/a['getCalls']if a['getCalls']else 0
 total={k:sum(a[k]for a in aggregate.values())for k in ['stores','getCalls','lastInsertedMatches','mapHits','newCalls','insertions']};total['predictedGetHitRate']=total['lastInsertedMatches']/total['getCalls']if total['getCalls']else 0
 entry={'name':name,'inputReport':'benchmarks/results/'+('lazy-default'if name=='trpc'else'lazy-default-large')+'.json','inputCommit':p['commit'],'fileListSha256':p['preflight']['candidate']['fileListSha256'],'cwd':p['cwd'],'command':args,'profileEnvironment':{'TSC_GO_LINKSTORE_PROFILE':str(prefix)},'exitCode':code,'expectedExitCode':p['expectedExit'],'stdoutSha256':hashlib.sha256(stdout).hexdigest(),'stderrSha256':hashlib.sha256(stderr).hexdigest(),'rawProfiles':[{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in paths],'totals':total,'byStoreType':dict(sorted(aggregate.items(),key=lambda x:-x[1]['getCalls']))};out['runs'].append(entry);(copy/'report.json').write_text(json.dumps(out,indent=2)+'\n');print('DONE',name,code,'Get hitrate',total['predictedGetHitRate'],flush=True)
 if code!=p['expectedExit']:break
