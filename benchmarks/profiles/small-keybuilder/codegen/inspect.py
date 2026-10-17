from pathlib import Path
import subprocess,json,hashlib,re,sys
ROOT=Path('/home/dev/tssss/tsc-tsgo');OUT=Path('/tmp/tsc-small-keybuilder-codegen');GO='/tmp/tsc-toolchains/go/bin/go'
paths={'baseline':ROOT/'packages/tsc-go/dist/tsc-go-pointer-linkstore','candidate':Path(sys.argv[1])}
commands=[]
def run(args):
 commands.append(args)
 return subprocess.check_output(args,cwd=ROOT,text=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
meta={'scope':'Bounded static production-code inspection; no compiler rebuild or performance measurement','commands':commands,'binaries':{}}
helper=r'checker\.(getRelationKey|getIndexedAccessKey|getTypeListKey|getConditionalTypeKey|\(\*keyBuilder\)\.(hash|stream|writeBytes|writeString|writeByte|writeUint32|writeUint64))$'
caller=r'checker\.\(\*Checker\)\.instantiateTypeWithAlias$'
for label,p in paths.items():
 side=Path(str(p)+'.provenance.json');s=json.loads(side.read_text())
 meta['binaries'][label]={'path':str(p),'sha256':sha(p),'sidecarSha256':sha(side),'source':{k:s['source'][k] for k in ('revision','dirty','sha256')},'sourceFileCount':len(s['source']['files']),'build':s['build']}
 nm=run([GO,'tool','nm','-size',str(p)])
 (OUT/(label+'-symbols.txt')).write_text('\n'.join(l for l in nm.splitlines() if re.search(helper+'|'+caller,l))+'\n')
 helpers=run([GO,'tool','objdump','-s',helper,str(p)])
 (OUT/(label+'-helpers.asm')).write_text(helpers)
 asm=run([GO,'tool','objdump','-s',caller,str(p)]).splitlines();keep=set()
 for i,line in enumerate(asm):
  if line.startswith('TEXT '):keep.update(range(i,min(i+14,len(asm))))
  if re.search(r'CALL .*?(keyBuilder|xxh3|hashWrite|newobject|duffzero)|MOVUPS X15',line):keep.update(range(max(0,i-8),min(i+8,len(asm))))
 out=[];last=-2
 for i in sorted(keep):
  if i!=last+1:out.append('  ... [unrelated caller instructions omitted] ...')
  out.append(asm[i]);last=i
 (OUT/(label+'-caller.asm')).write_text('\n'.join(out)+'\n')
 meta['binaries'][label]['sha256After']=sha(p)
meta['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in OUT.iterdir() if p.suffix in ('.asm','.txt')}
(OUT/'capture.json').write_text(json.dumps(meta,indent=2)+'\n')
print('Bounded inspection terminal; no compiler build performed')
