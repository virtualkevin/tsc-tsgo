from pathlib import Path
import hashlib,json,re,subprocess
here=Path(__file__).resolve().parent;root=here.parents[2];go='/tmp/tsc-toolchains/go/bin/go';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
build=json.loads((here/'build.json').read_text());items=[]
for role,filename,digest in [('baseline','tsc-go-node-pointer','8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f'),('candidate','tsc-go-tagged-node-data',build['binarySha256'])]:
 binary=root/'packages/tsc-go/dist'/filename;assert sha(binary)==digest
 names=[('newNode','newNode'),('NewIdentifier',r'\(\*NodeFactory\)\.NewIdentifier')]
 if role=='candidate':names += [('nodeDataValue',r'\(\*Node\)\.nodeDataValue'),('setNodeData',r'\(\*Node\)\.setNodeData')]
 for name,pattern in names:
  command=[go,'tool','objdump','-s',r'github.com/microsoft/typescript-go/internal/ast\.'+pattern+'$',str(binary)]
  p=subprocess.run(command,capture_output=True,text=True,check=True);assert not p.stderr and p.stdout.startswith('TEXT ')
  output=role+'-'+name+'.asm.txt';(here/output).write_text(p.stdout)
  rows=[line for line in p.stdout.splitlines() if re.match(r'^\s+\S+:\d+\s+0x[0-9a-f]+\s+[0-9a-f]+\s+',line)]
  stack=re.search(r'SUBQ \$0x([0-9a-f]+), SP',p.stdout)
  items.append(dict(role=role,function=name,command=command,toolSha256=sha(go),binarySha256=digest,output=output,outputSha256=sha(here/output),instructionRows=len(rows),encodedInstructionBytes=sum(len(line.split()[2])//2 for line in rows),entryStackReservationBytes=int(stack[1],16) if stack else None))
(here/'codegen.json').write_text(json.dumps(items,indent=2)+'\n')
print(json.dumps([{k:v for k,v in x.items() if k in ['role','function','encodedInstructionBytes','entryStackReservationBytes']} for x in items]))
