"""Static compiled code only; no execution timing or speedup inference."""
from pathlib import Path
import hashlib,json,re,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2]
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
build=json.loads((p/'build.json').read_text());freeze=json.loads((p/'cli-freeze.json').read_text())
assert build['exitCode']==0 and build['sources']==freeze['sources']
go='/tmp/tsc-fused-objdump/objdump'
binaries={'baseline':r/'packages/tsc-go/dist/tsc-go-node-pointer','candidate':Path('/tmp/tsc-fused-intersection-lookup-validation/tsc-fused-intersection-lookup')}
assert sha(binaries['baseline'])=='8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f'
assert sha(binaries['candidate'])==build['binarySha256']
pattern=r'checker\.\(\*Checker\)\.getTypeOfPropertyOfType$|checker\.cachedIntersectionProperty$'
report={'scope':'Static code size/call sites, not executed instruction counts, timing, CPU budget or speedup. Absent standalone helper does not by itself prove every call was inlined.','controllerSha256':sha(__file__),'goSha256':sha(go),'buildSha256':sha(p/'build.json'),'binaries':{}}
for label,binary in binaries.items():
 cmd=[go,'-s',pattern,str(binary)]
 raw=subprocess.check_output(cmd);out=p/(label+'-lookup.asm');out.write_bytes(raw)
 functions={};current=None
 for line in raw.decode().splitlines():
  if line.startswith('TEXT '):
   current=line.split()[1];functions[current]={'encodedBytes':0,'instructions':0,'calls':[]}
  else:
   fields=line.split()
   if len(fields)>=4 and re.fullmatch(r'0x[0-9a-f]+',fields[1]) and re.fullmatch(r'[0-9a-f]+',fields[2]):
    assert current is not None
    functions[current]['encodedBytes']+=len(fields[2])//2;functions[current]['instructions']+=1
    if fields[3]=='CALL':functions[current]['calls'].append(' '.join(fields[4:]))
 assert any('getTypeOfPropertyOfType' in name for name in functions)
 report['binaries'][label]={'sha256':sha(binary),'command':cmd,'assemblySha256':sha(out),'functions':functions}
(p/'codegen.json').write_text(json.dumps(report,indent=2)+'\n')
for label,data in report['binaries'].items():print(label,json.dumps(data['functions']))
