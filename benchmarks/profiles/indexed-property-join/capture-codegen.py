from pathlib import Path
import hashlib,json,re,subprocess
here=Path(__file__).resolve().parent;root=here.parents[2];go='/tmp/tsc-toolchains/go/bin/go'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
build=json.loads((here/'build.json').read_text());binary=root/'packages/tsc-go/dist/tsc-go-indexed-property-join';assert sha(binary)==build['binarySha256']
items=[]
for name in ['propertiesRelatedTo','indexedPropertiesRelatedTo','nextIndexedProperty']:
 command=[go,'tool','objdump','-s',r'github.com/microsoft/typescript-go/internal/checker\.\(\*'+('Checker' if name=='nextIndexedProperty' else 'Relater')+r'\)\.'+name+'$',str(binary)]
 p=subprocess.run(command,capture_output=True,text=True,check=True);assert not p.stderr and p.stdout.startswith('TEXT ')
 output=name+'.asm.txt';(here/output).write_text(p.stdout)
 rows=[line for line in p.stdout.splitlines() if re.match(r'^\s+\S+:\d+\s+0x[0-9a-f]+\s+[0-9a-f]+\s+',line)]
 items.append(dict(function=name,command=command,toolSha256=sha(go),binarySha256=sha(binary),output=output,outputSha256=sha(here/output),instructionRows=len(rows),encodedInstructionBytes=sum(len(line.split()[2])//2 for line in rows),entryStackReservationBytes=int(re.search(r'SUBQ \$0x([0-9a-f]+), SP',p.stdout)[1],16)))
(here/'codegen.json').write_text(json.dumps(items,indent=2)+'\n')
print(json.dumps([{k:v for k,v in x.items() if k in ['function','instructionRows','encodedInstructionBytes','entryStackReservationBytes']} for x in items]))
