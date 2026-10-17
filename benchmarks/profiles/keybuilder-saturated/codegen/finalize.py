import json,hashlib,re,pathlib
p=pathlib.Path('/tmp/tsc-keybuilder-saturated-codegen'); repo=pathlib.Path('/home/dev/tssss/tsc-tsgo')
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

out('summary.json',{'scope':'Production codegen and isolated primitive allocation only; no compiler performance measurement','binaries':capture['binaries'],'framesExcludingSavedBP':frames,'symbolCodeBytes':symbols,'findings':['All three primitive writer helpers are inlined in production: no emitted helper symbols, direct byte/integer stores at selected callers. Tiny-package inline cost76 each.','First two fixed-offset indexed-access uint32 writes have no guards/bounds checks; the third still checks capacity and bounds. General relation/alias writes retain bounds checks.','Cold overflow calls remain; stream now saturates n after copying the prefix. No buffer representation change.','Inlining increases some caller code sizes; getRelationKey367 to684 bytes. No runtime conclusion follows.','Same51 allocation cases pass with unchanged counts: zero through128, one above128, zero prepared-hash/indexed-map-hit.'],'allocationScreen':'allocation-summary.json','sourceComparison':'source-comparison.json','allProcessesTerminal':True,'compilerRebuiltByInspection':False})
prep=json.loads((p/'preparation.json').read_text());prep['commandsExecuted']=True;out('preparation.json',prep)
print(json.dumps(frames,indent=2))
