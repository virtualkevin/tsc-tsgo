from pathlib import Path
import hashlib,json,re
p=Path('/tmp/tsc-prehashed-relation-codegen');capture=json.loads((p/'capture.json').read_text())
def out(name,value): (p/name).write_text(json.dumps(value,indent=2)+'\n')
sides={label:json.loads(Path(b['path']+'.provenance.json').read_text()) for label,b in capture['binaries'].items()};files={k:{f['path']:f for f in side['source']['files']} for k,side in sides.items()};diffs=[{'path':k,'baseline':files['baseline'].get(k),'candidate':files['candidate'].get(k)} for k in sorted(files['baseline'].keys()|files['candidate'].keys()) if files['baseline'].get(k)!=files['candidate'].get(k)]
assert [d['path'].rsplit('/',1)[1] for d in diffs]==['relater.go','relation_results.go','relation_results_test.go'];assert sides['baseline']['build']==sides['candidate']['build']
out('source-comparison.json',{'baselineSource':capture['binaries']['baseline']['source'],'candidateSource':capture['binaries']['candidate']['source'],'buildSettingsEqual':True,'differences':diffs})
frames={};symbols={};calls={}
for label in sides:
 frames[label]={};calls[label]={}
 for suffix in ['helpers','callers']:
  for section in (p/(label+'-'+suffix+'.asm')).read_text().split('TEXT ')[1:]:
   name=section.split('(SB)',1)[0].split('/checker.')[-1];frame=re.search(r'SUBQ \$0x([0-9a-f]+), SP',section)
   if frame:frames[label][name]=int(frame.group(1),16)
   calls[label][name]=sorted(set(re.findall(r'CALL ([^\s]+)',section)))
 symbols[label]={line.split()[-1].split('/checker.')[-1]:int(line.split()[1]) for line in (p/(label+'-symbols.txt')).read_text().splitlines()}
out('summary.json',{'scope':'Read-only production objdump evidence; no runtime or allocation measurement','binaries':capture['binaries'],'framesExcludingSavedBP':frames,'symbolCodeBytes':symbols,'callsInCapturedExcerpts':calls,'findings':['Relation wrappers inline but cache get/set/rebuild remain calls. find/bitmap/slot helpers are inlined into these methods.','Table get directly masks prehash low bits, tests occupancy with BTQ, compares both64-bit key words, and loads uint32 value. Bitmap, key and value bounds checks remain.','Fallback get/set use runtime.mapaccess1/mapassign; table path does not rehash key via runtime.','New table allocation emits three makeslice calls; bulk store changes retain write barrier operations. No allocation amount or escape rate inferred.','useFallback is inlined into multiple failure branches, contributing code size to set/rebuild. resetMaybeStack is out of line in candidate, whereas baseline body was inline at inspected callers.'],'sourceComparison':'source-comparison.json','allProcessesTerminal':True,'compilerRebuilt':False,'testsRun':False,'workloadsRun':False})
print(json.dumps(frames,indent=2))
