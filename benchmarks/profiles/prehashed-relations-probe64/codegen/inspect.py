from pathlib import Path
import hashlib,json,re,subprocess,sys
root=Path('/home/dev/tssss/tsc-tsgo');out=Path('/tmp/tsc-prehashed-relation-codegen');go='/tmp/tsc-toolchains/go/bin/go'
paths={'baseline':root/'packages/tsc-go/dist/tsc-go-keybuilder-saturated','candidate':Path(sys.argv[1])}
helpers=r'checker\.(\(\*relationResultCache\)\.(get|size|hasSlot|find|writeSlot|set|rebuild|useFallback)|\(\*Relation\)\.(get|set|size)|nextRelationResultCapacity|newRelationResultTable)$'
callers=r'checker\.(\(\*Checker\)\.isTypeRelatedTo|\(\*Relater\)\.(recursiveTypeRelatedTo|resetMaybeStack))$'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
meta={'scope':'Bounded codegen inspection only; no compiler rebuild, workload, timing or allocation measurement','commands':[],'binaries':{}}
def run(args):
 meta['commands'].append(args)
 return subprocess.check_output(args,cwd=root,text=True)
for label,binary in paths.items():
 side=Path(str(binary)+'.provenance.json');p=json.loads(side.read_text())
 assert sha(binary)==p['binary']['sha256']
 meta['binaries'][label]={'path':str(binary),'sha256':sha(binary),'sidecarSha256':sha(side),'source':{k:p['source'][k] for k in ['revision','dirty','sha256']},'sourceFileCount':len(p['source']['files']),'build':p['build']}
 nm=run([go,'tool','nm','-size',str(binary)])
 (out/(label+'-symbols.txt')).write_text('\n'.join(l for l in nm.splitlines() if re.search(helpers+'|'+callers,l))+'\n')
 (out/(label+'-helpers.asm')).write_text(run([go,'tool','objdump','-s',helpers,str(binary)]))
 lines=run([go,'tool','objdump','-s',callers,str(binary)]).splitlines();keep=set()
 for i,line in enumerate(lines):
  if line.startswith('TEXT '):keep.update(range(i,min(len(lines),i+14)))
  if re.search(r'relation_results.go:|CALL .*?(relationResultCache|Relation\)|mapaccess|mapassign|makemap|makeslice|newobject)',line):keep.update(range(max(0,i-6),min(len(lines),i+8)))
 selected=[];last=-2
 for i in sorted(keep):
  if i!=last+1:selected.append(' ... [unrelated caller instructions omitted] ...')
  selected.append(lines[i]);last=i
 (out/(label+'-callers.asm')).write_text('\n'.join(selected)+'\n')
 assert sha(binary)==meta['binaries'][label]['sha256']
meta['artifacts']={f.name:{'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(out.iterdir()) if f.suffix in ['.asm','.txt']}
(out/'capture.json').write_text(json.dumps(meta,indent=2)+'\n')
print('Inspection terminal; no compiler build/workload executed')
