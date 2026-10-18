from pathlib import Path
import hashlib,json,subprocess,re
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
config=json.loads((out/'screen.json').read_text());report={'scope':'Static encoded function bodies, not runtime, allocations, or speedup evidence. Inlined functions may have no standalone body.','binaries':{}}
for label in ['baseline','candidate']:
 entry=config['expected'][label];binary=Path(entry['path']);assert sha(binary)==entry['sha256']
 functions={}
 for method in ['newObjectType','getSignaturesOfStructuredType','setStructuredTypeMembers']:
  pattern=r'github.com/microsoft/typescript-go/internal/checker\.\(\*Checker\)\.'+method+'$'
  result=subprocess.run(['/tmp/tsc-toolchains/go/bin/go','tool','objdump','-s',pattern,str(binary)],text=True,capture_output=True,check=True)
  assert not result.stderr
  p=out/(label+'-'+method+'.asm.txt');p.write_text(result.stdout)
  encodings=re.findall(r'^\s*\S+\s+0x[0-9a-f]+\s+([0-9a-f]+)\s+',result.stdout,re.M)
  functions[method]={'encodedBytes':sum(len(x)//2 for x in encodings),'hasStandaloneBody':bool(encodings),'sha256':sha(p)}
 report['binaries'][label]={'sha256':entry['sha256'],'functions':functions}
(out/'codegen.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
