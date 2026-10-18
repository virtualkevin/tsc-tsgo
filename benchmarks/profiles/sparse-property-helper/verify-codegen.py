from pathlib import Path
import hashlib,json,re,subprocess
here=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for item in json.loads((here/'codegen.json').read_text()):
 assert sha(item['command'][0])==item['toolSha256']
 assert sha(item['command'][-1])==item['binarySha256']
 p=subprocess.run(item['command'],capture_output=True,text=True,check=True);assert not p.stderr
 data=p.stdout.encode();assert hashlib.sha256(data).hexdigest()==item['outputSha256'];assert data==(here/item['output']).read_bytes()
 rows=[line for line in p.stdout.splitlines() if re.match(r'^\s+\S+:\d+\s+0x[0-9a-f]+\s+[0-9a-f]+\s+',line)]
 assert len(rows)==item['instructionRows']
 assert sum(len(line.split()[2])//2 for line in rows)==item['encodedInstructionBytes']
 assert int(re.search(r'SUBQ \$0x([0-9a-f]+), SP',p.stdout)[1],16)==item['entryStackReservationBytes']
 print(item['function'],'exact reproduction passed')
