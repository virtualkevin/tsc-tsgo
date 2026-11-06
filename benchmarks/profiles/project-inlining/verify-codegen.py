from pathlib import Path
import gzip,hashlib,json,subprocess
p=Path(__file__).resolve().parent
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
r=json.loads((p/'codegen.json').read_text())
assert r['controllerSha256']==sha(p/'codegen.py') and r['buildReportSha256']==sha(p/'build.json')
assert [x['side'] for x in r['runs']]==['retained','candidate']
for x in r['runs']:
 assert sha(x['binary'])==x['binarySha256'] and Path(x['binary']).stat().st_size==x['binaryBytes']
 assert sha(x['command'][0])==r['toolSha256']
 archive=p/x['archive'];raw=gzip.decompress(archive.read_bytes())
 assert sha(archive)==x['archiveSha256'] and hashlib.sha256(raw).hexdigest()==x['rawSha256']
 assert subprocess.check_output(x['command'],timeout=120)==raw
 names=[line[5:line.index('(SB)')+4] for line in raw.decode().splitlines() if line.startswith('TEXT ')]
 assert len(names)==len(set(names)) and set(names)==set(x['functions'])
a,b=r['runs'];key='github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol(SB)'
assert any('PointerLinkStore[' in k and k.endswith(']).Get(SB)') for k in a['functions'][key]['calls'])
assert not any('PointerLinkStore[' in k and k.endswith(']).Get(SB)') for k in b['functions'][key]['calls'])
assert any('PointerLinkStore[' in k and k.endswith(']).slot(SB)') for k in b['functions'][key]['calls'])
assert a['functions'][key]['instructionBytes']==180 and b['functions'][key]['instructionBytes']==309
report={'passed':True,'codegenReportSha256':sha(p/'codegen.json'),'verifierSha256':sha(__file__),'binaryGrowthPercent':100*(b['binaryBytes']/a['binaryBytes']-1),'scope':'Exact disassembly reproduction, binary/archive hashes, full symbol-name sets and selected caller transition; not performance or whole-program inlining proof.'}
with (p/'codegen-readback.json').open('x') as f:f.write(json.dumps(report,indent=2)+'\n')
print('Disassembly readback and selected caller checks passed')
