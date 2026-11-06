"""Bounded disassembly evidence from actual normal executables, not timing."""
from pathlib import Path
import gzip,hashlib,json,re,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2]
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
build=json.loads((p/'build.json').read_text());assert build['passed']
binaries={'retained':r/'packages/tsc-go/dist/tsc-go','candidate':Path(build['binary'])}
hashes={'retained':'8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f','candidate':build['binarySha256']}
tool='/tmp/tsc-fused-objdump/objdump'
pattern=r'checker\.\(\*Checker\)\.(newType|getTypeOfSymbol|getTypeOfInstantiatedSymbol|instantiateType|getPropertyOfType)$|core\.\(\*PointerLinkStore.*\)\.(Get|slot)$'
report={'scope':'Bounded actual executable disassembly and file size; no whole-program inlining, performance or correctness claim. Missing emitted symbols alone do not prove every call inlines.','controllerSha256':sha(__file__),'buildReportSha256':sha(p/'build.json'),'toolSha256':sha(tool),'pattern':pattern,'runs':[]}
for side,binary in binaries.items():
 assert sha(binary)==hashes[side]
 command=[tool,'-s',pattern,str(binary)];target=p/(side+'-selected.asm.gz')
 if target.exists():
  failure=json.loads((p/'codegen-parser-failure.json').read_text())
  assert side=='retained' and sha(target)==failure['preservedArchiveSha256']
  raw=gzip.decompress(target.read_bytes())
 else:
  raw=subprocess.check_output(command,timeout=120)
  with target.open('xb') as f:
   with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as g:g.write(raw)
 assert raw and sha(binary)==hashes[side] and gzip.decompress(target.read_bytes())==raw
 functions={};current=None
 for line in raw.decode().splitlines():
  if line.startswith('TEXT '):
   assert '(SB)' in line
   current=line[5:].split('(SB)',1)[0]+'(SB)';assert current not in functions
   functions[current]={'instructionBytes':0,'instructions':0,'calls':{}}
  elif current:
   m=re.match(r'^\s+\S+\s+0x[0-9a-f]+\s+([0-9a-f]+)\s+(.*)$',line)
   if not m:continue
   code,ins=m.groups();assert len(code)%2==0
   entry=functions[current];entry['instructionBytes']+=len(code)//2;entry['instructions']+=1
   if ins.startswith('CALL '):
    call=ins[5:].strip();entry['calls'][call]=entry['calls'].get(call,0)+1
 assert functions and all(f['instructions']>0 for f in functions.values())
 report['runs'].append({'side':side,'binary':str(binary),'binarySha256':hashes[side],'binaryBytes':binary.stat().st_size,'command':command,'archive':target.name,'archiveSha256':sha(target),'rawSha256':hashlib.sha256(raw).hexdigest(),'functions':functions})
with (p/'codegen.json').open('x') as f:f.write(json.dumps(report,indent=2)+'\n')
for run in report['runs']:print(run['side'],run['binaryBytes'],'binary bytes;',len(run['functions']),'selected emitted symbols;',sum(x['instructionBytes'] for x in run['functions'].values()),'selected instruction bytes')
