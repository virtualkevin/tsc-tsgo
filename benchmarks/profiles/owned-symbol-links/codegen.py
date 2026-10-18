from pathlib import Path
import hashlib,json,re,subprocess
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent/'codegen';out.mkdir(exist_ok=True)
config=json.loads((out.parent/'screen.json').read_text());report={}
functions=['getTypeOfInstantiatedSymbol','newInstantiatedSymbolWithLinks','getTypeOfMappedSymbol']
for role in ['baseline','candidate']:
 binary=Path(config['expected'][role]['path']);digest=hashlib.sha256(binary.read_bytes()).hexdigest();assert digest==config['expected'][role]['sha256']
 result={'binarySha256':digest,'functions':{}}
 for name in functions:
  pattern=r'.*checker\.\(\*Checker\)\.'+name+'$'
  command=['/tmp/tsc-toolchains/go/bin/go','tool','objdump','-s',pattern,str(binary)]
  p=subprocess.run(command,capture_output=True,check=True,text=True);assert p.stdout.startswith('TEXT ')
  file=out/(role+'-'+name+'.txt');file.write_text(p.stdout)
  instructions=[]
  for line in p.stdout.splitlines():
   m=re.match(r'^\s*\S+\s+0x[0-9a-f]+\s+([0-9a-f]+)\s+(.*)$',line)
   if m:instructions.append((m[1],m[2]))
  assert instructions
  result['functions'][name]={'command':command,'assemblySha256':hashlib.sha256(file.read_bytes()).hexdigest(),'instructions':len(instructions),'instructionBytes':sum(len(x)//2 for x,_ in instructions),'calls':[text for _,text in instructions if text.startswith('CALL ')]}
 report[role]=result
report['scope']='Static generated code, not measured CPU cycles, cache behavior, runtime speedup or complete symbol-store cost. Representative callers only; out-of-line callees excluded from byte counts.'
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
for name in functions:print(name,report['baseline']['functions'][name]['instructionBytes'],report['candidate']['functions'][name]['instructionBytes'])
