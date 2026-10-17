import json,hashlib,re,pathlib
p=pathlib.Path('/tmp/tsc-keybuilder-direct-codegen'); repo=pathlib.Path('/home/dev/tssss/tsc-tsgo')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def out(n,o): (p/n).write_text(json.dumps(o,indent=2)+'\n')
capture=json.loads((p/'capture.json').read_text()); sides={k:json.loads(pathlib.Path(v['path']+'.provenance.json').read_text()) for k,v in capture['binaries'].items()}
files={k:{f['path']:f for f in v['source']['files']} for k,v in sides.items()}
diffs=[{'path':k,'baseline':files['baseline'].get(k),'candidate':files['candidate'].get(k)} for k in sorted(files['baseline'].keys()|files['candidate'].keys()) if files['baseline'].get(k)!=files['candidate'].get(k)]
assert [d['path'].split('/')[-1] for d in diffs]==['keybuilder.go','keybuilder_direct_test.go']
assert sides['baseline']['build']==sides['candidate']['build']
out('source-comparison.json',{'baselineSource':capture['binaries']['baseline']['source'],'candidateSource':capture['binaries']['candidate']['source'],'buildSettingsEqual':True,'differences':diffs,'productionDifferences':['packages/tsc-go/internal/checker/keybuilder.go'],'testDifferences':['packages/tsc-go/internal/checker/keybuilder_direct_test.go']})
a=json.loads(pathlib.Path('/tmp/tsc-small-keybuilder-codegen/allocation-summary.json').read_text()); src=repo/'packages/tsc-go/internal/checker/keybuilder.go'; copy=p/'allocation-screen/keybuilder.go'
assert sha(src)==sha(copy)==files['candidate']['packages/tsc-go/internal/checker/keybuilder.go']['sha256']
a['source'].update(path=str(src),sha256=sha(src),verbatimCopy=str(copy),copySha256=sha(copy));
for c in a['commands']: c['cwd']=str(p/'allocation-screen')
results={}; current=None
for line in (p/'allocation.log').read_text().splitlines():
 if line.startswith('=== RUN   TestAllocationScreen/'): current=line.split('TestAllocationScreen/',1)[1]
 if 'allocations_per_call=' in line: results[current]=float(line.split('allocations_per_call=')[1])
assert len(results)==51 and results==a['allocationsPerCall']; a['allocationsPerCall']=results
out('allocation-summary.json',a)
frames={}; symbols={}
for side in ['baseline','candidate']:
 txt=(p/(side+'-helpers.asm')).read_text()+'\n'+(p/(side+'-caller.asm')).read_text()
 frames[side]={}
 for section in txt.split('TEXT ')[1:]:
  name=section.split('(SB)',1)[0].split('/checker.')[-1]; frame=re.search(r'SUBQ \$0x([0-9a-f]+), SP',section)
  if frame: frames[side][name]=int(frame.group(1),16)
 symbols[side]={line.split()[-1].split('/checker.')[-1]:int(line.split()[1]) for line in (p/(side+'-symbols.txt')).read_text().splitlines()}
compiler=pathlib.Path('/tmp/tsc-toolchains/go/src/cmd/compile/internal/inline/inl.go')
lines=compiler.read_text().splitlines(); (p/'compiler-budget-excerpt.txt').write_text('\n'.join(f'{i+1}: {lines[i]}' for i in range(807,820))+'\n')
out('summary.json',{'scope':'Production assembly and isolated primitive allocation evidence only; no compiler speed or total allocation improvement claim','binaries':capture['binaries'],'sourceComparison':'source-comparison.json','framesExcludingSavedBP':frames,'symbolCodeBytes':symbols,'findings':['All three dedicated primitive writer methods remain out of line in the production binary. Tiny-package -m=2 reports cost 81 against budget 80; this is not a claim that a one-node edit will make them inline.','Go inl.go line 814 disables early budget termination under -m=2; the captured diagnostic is the completed accounting for this screen.','The integer writer short branches use direct MOVL/MOVQ stores instead of calling generic writeBytes and runtime.memmove. Caller-to-writer calls remain.','writeBytes has no emitted production symbol; it remains reachable in the isolated test screen. writeString still uses memmove.','Both versions retain the 144-byte builder and same streaming overflow strategy. Short screen cases allocate zero; overflow cases allocate once. This does not establish that every compiler cache-hit path allocates zero.'],'allocationScreen':'allocation-summary.json','compilerBudgetSource':{'path':str(compiler),'sha256':sha(compiler),'excerpt':'compiler-budget-excerpt.txt'},'allProcessesTerminal':True,'compilerRebuiltByInspection':False})
prep=json.loads((p/'preparation.json').read_text()); prep['commandsExecuted']=True; out('preparation.json',prep)
