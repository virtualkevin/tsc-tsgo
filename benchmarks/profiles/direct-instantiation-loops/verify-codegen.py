from pathlib import Path
import hashlib,json,re,subprocess
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
r=json.loads((p/'codegen.json').read_text());assert r['status']=='passed' and r['controllerSha256']==sha(p/'build-codegen.py')
rows=[]
for run in r['runs']:
 assert run['exitCode']==0 and sha(run['binary'])==run['binarySha256']
 assert sha(run['command'][0])==run['toolchainSha256'] and sha(run['objdumpCommand'][0])==run['objdumpSha256']
 overlay=json.loads(Path(run['command'][4]).read_text())['Replace'];assert run['sources']=={k:sha(v) for k,v in overlay.items()}
 path=p/(run['prefix']+'assembly.txt');assert sha(path)==run['assemblySha256']
 assert subprocess.check_output(run['objdumpCommand'])==path.read_bytes()
 sections={}
 for block in path.read_text().split('TEXT ')[1:]:
  name,body=block.split('\n',1);sections[name.split('(SB)')[0]]=body
 for plural,singular in [('Types','TypeWithAlias'),('Symbols','Symbol'),('Signatures','SignatureEx'),('IndexInfos','IndexInfo')]:
  if not run['prefix']:
   key=next(k for k in sections if k.endswith('(*Checker).instantiate'+plural));body=sections[key]
   assert not re.search(r'\bCALL (?:AX|BX|CX|DX|DI|SI|R\d+)\b',body)
   assert body.count('CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiate'+singular+'(SB)')==2
   lines=[l for l in body.splitlines() if l.strip()];sizes=[len(l.split()[2])//2 for l in lines]
   rows.append({'function':plural,'instructions':len(lines),'instructionBytes':sum(sizes),'indirectCalls':0,'directInstantiationCallsites':2})
  else:
   typ={'Types':'Type','Symbols':'Symbol','Signatures':'Signature','IndexInfos':'IndexInfo'}[plural]
   key=next(k for k in sections if 'instantiateList[' in k and k.endswith('/'+('ast' if typ=='Symbol' else 'checker')+'.'+typ+']'));body=sections[key]
   assert len(re.findall(r'\bCALL DI\b',body))==2
print(json.dumps({'passed':True,'buildReportSha256':sha(p/'codegen.json'),'directLoops':rows,'baseline':'Each of four generic loops has two indirect CALL DI sites. Baseline wrappers were inlined; candidate wrappers now have bodies.','scope':'Pinned normal test-binary assembly; no performance or production executable claim.','verifierSha256':sha(__file__)},indent=2))
