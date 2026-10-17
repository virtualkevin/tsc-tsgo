from pathlib import Path
import subprocess, json, hashlib, sys, re
ROOT=Path('/home/dev/tssss/tsc-tsgo')
OUT=Path('/tmp/tsc-relation-keys-codegen')
GO='/tmp/tsc-toolchains/go/bin/go'
paths={'baseline':ROOT/'packages/tsc-go/dist/tsc-go-pointer-linkstore','candidate':Path(sys.argv[1])}
commands=[]
def run(args):
 commands.append(args)
 return subprocess.check_output(args,cwd=ROOT,text=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
metadata={'scope':'Targeted static code generation; no compilation, runtime profiling, or benchmark','binaries':{},'commands':commands}
pattern=r'checker\.(getRelationKey|\(\*Checker\)\.(getRelationKey|getHashedRelationKey|internRelationHash|isTypeRelatedTo)|\(\*Relater\)\.(recursiveTypeRelatedTo|resetMaybeStack)|\(\*Relation\)\.(get|set))$'
for label,p in paths.items():
 side=Path(str(p)+'.provenance.json'); prov=json.loads(side.read_text())
 metadata['binaries'][label]={'path':str(p),'sha256':sha(p),'sidecarSha256':sha(side),'provenanceKeys':list(prov)}
 nm=run([GO,'tool','nm','-size',str(p)])
 (OUT/(label+'-symbols.txt')).write_text('\n'.join(l for l in nm.splitlines() if re.search(pattern,l))+'\n')
 helpers=run([GO,'tool','objdump','-s',r'checker\.(getRelationKey|\(\*Checker\)\.(getRelationKey|getHashedRelationKey|internRelationHash))$',str(p)])
 (OUT/(label+'-keys.asm')).write_text(helpers)
 callers=run([GO,'tool','objdump','-s',r'checker\.(\(\*Checker\)\.isTypeRelatedTo|\(\*Relater\)\.(recursiveTypeRelatedTo|resetMaybeStack)|\(\*Relation\)\.(get|set))$',str(p)])
 lines=callers.splitlines();keep=set()
 for i,line in enumerate(lines):
  if line.startswith('TEXT '):keep.update(range(i,min(i+12,len(lines))))
  if re.search(r'CALL .*?(getRelationKey|getHashedRelationKey|internRelationHash|mapaccess|mapassign|makemap|Relation\)\.(get|set)|memhash)',line):keep.update(range(max(0,i-10),min(i+6,len(lines))))
 snippets=[];last=-2
 for i in sorted(keep):
  if i!=last+1:snippets.append('  ... [unrelated caller instructions omitted] ...')
  snippets.append(lines[i]);last=i
 (OUT/(label+'-callers.asm')).write_text('\n'.join(snippets)+'\n')
 metadata['binaries'][label]['sha256After']=sha(p)
metadata['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in OUT.iterdir() if p.suffix in ('.asm','.txt')}
(OUT/'capture.json').write_text(json.dumps(metadata,indent=2)+'\n')
print('Static capture complete; all subprocesses terminal')
