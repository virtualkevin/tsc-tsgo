"""Check exact regeneration and rejection of unknown layouts in a private copy."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile
here=Path(__file__).resolve().parent
profile=here.parent
root=profile.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=['internal/ast/ast_generated.go','internal/api/encoder/encoder_generated.go','internal/ast/canonical_names_generated.go']
command=['python3',str(here/'generate-name-storage.py'),'--gofmt','/tmp/tsc-toolchains/go/bin/gofmt']
report={'scope':'Local post-generation storage adaptation and constant-pool reproducibility; not a rerun of the upstream generators or compiler correctness/performance evidence.','passed':False,'generatorSha256':sha(here/'generate-name-storage.py'),'schemaSha256':sha(here/'canonical-names.json')}
with tempfile.TemporaryDirectory(prefix='tsc-canonical-generation-') as temp:
 destination=Path(temp)
 for rel in paths[:2]:
  target=destination/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/'packages/tsc-go'/rel,target)
 report['baselineInputs']={rel:sha(destination/rel) for rel in paths[:2]}
 subprocess.run([*command,'--root',str(destination),'--write'],check=True,capture_output=True,text=True)
 for rel in paths:assert sha(destination/rel)==sha(profile/'staged'/rel)
 first={rel:sha(destination/rel) for rel in paths}
 subprocess.run([*command,'--root',str(destination),'--write'],check=True,capture_output=True,text=True)
 subprocess.run([*command,'--root',str(destination)],check=True,capture_output=True,text=True)
 assert first=={rel:sha(destination/rel) for rel in paths}
 report['generatedOutputs']=first
 bad=destination/paths[0];text=bad.read_text();needle='FlowNodeBase\n\tText Name';assert text.count(needle)==1;bad.write_text(text.replace(needle,'FlowNodeBase\n\tText []byte',1))
 before={rel:sha(destination/rel) for rel in paths}
 rejected=subprocess.run([*command,'--root',str(destination),'--write'],capture_output=True,text=True)
 assert rejected.returncode!=0 and 'unrecognized generated source layout' in rejected.stderr
 assert before=={rel:sha(destination/rel) for rel in paths}
 report['unknownLayoutRejectedWithoutWrites']=True
report['passed']=True
(here/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'generatedFiles':len(paths),'idempotent':True,'unknownLayoutRejectedWithoutWrites':True}))
