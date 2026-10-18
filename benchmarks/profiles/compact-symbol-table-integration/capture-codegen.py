from pathlib import Path
import hashlib,json,re,subprocess
root=Path(__file__).resolve().parents[3];out=Path(__file__).parent
go='/tmp/tsc-toolchains/go/bin/go'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
config=json.loads((out/'screen.json').read_text())
functions={
 'getResolvedMember':'github.com/microsoft/typescript-go/internal/checker.getResolvedMember',
 'getSymbol':'github.com/microsoft/typescript-go/internal/checker.(*Checker).getSymbol',
 'propertiesRelatedTo':'github.com/microsoft/typescript-go/internal/checker.(*Relater).propertiesRelatedTo',
}
report={'scope':'Static code generation only. Encoded bytes and stack reservations are not executed instruction counts, CPU costs, throughput or a speedup claim. Empty objdump output means no matching retained function, potentially due to inlining.','controllerSha256':sha(__file__),'functions':[]}
for label,fn in functions.items():
 record={'name':fn,'variants':{}}
 for variant in ['baseline','candidate']:
  e=config['expected'][variant];assert sha(e['path'])==e['sha256']
  command=[go,'tool','objdump','-s','^'+re.escape(fn)+'$',e['path']]
  data=subprocess.check_output(command,cwd=root);target=out/f'{variant}-{label}.asm.txt';target.write_bytes(data)
  lines=data.decode().splitlines();instructions=[];frames=[]
  for line in lines:
   m=re.search(r'\s0x[0-9a-f]+\s+([0-9a-f]+)\s+(.*)$',line)
   if not m:continue
   instructions.append(m.group(1));f=re.search(r'SUBQ \$(0x[0-9a-f]+|[0-9]+), SP',m.group(2))
   if f:frames.append(int(f.group(1),0))
  record['variants'][variant]={'command':command,'binarySha256':e['sha256'],'outputSha256':sha(target),'present':bool(data),'encodedInstructionBytes':sum(len(x)//2 for x in instructions),'disassembledInstructions':len(instructions),'stackReservations':frames}
 report['functions'].append(record)
(out/'codegen.json').write_text(json.dumps(report,indent=2)+'\n')
for r in report['functions']:print(r['name'],{k:{n:v[n] for n in ['present','encodedInstructionBytes','stackReservations']} for k,v in r['variants'].items()})
