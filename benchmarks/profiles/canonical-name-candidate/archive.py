"""Archive the staged candidate; never apply it to production sources."""
from pathlib import Path
import difflib,hashlib,json,shutil,subprocess
out=Path(__file__).resolve().parent
root=out.parents[2]
module=root/'packages/tsc-go'
stage=out/'staged'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=sorted(stage.rglob('*.go'))
patch=[]
for file in files:
 rel=file.relative_to(stage);base=module/rel
 patch.extend(difflib.unified_diff(base.read_text().splitlines(True) if base.exists() else [],file.read_text().splitlines(True),fromfile='a/packages/tsc-go/'+str(rel) if base.exists() else '/dev/null',tofile='b/packages/tsc-go/'+str(rel)))
(out/'candidate.patch').write_text(''.join(patch))
reconstruction=out/'reconstructed'
assert not reconstruction.exists(), 'do not overwrite an existing reconstruction'
for file in files:
 rel=file.relative_to(stage);base=module/rel
 if base.exists():
  target=reconstruction/'packages/tsc-go'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base,target)
subprocess.run(['git','apply','--directory='+str(reconstruction.relative_to(root)),str(out/'candidate.patch')],cwd=root,check=True)
for file in files:assert sha(file)==sha(reconstruction/'packages/tsc-go'/file.relative_to(stage))
source={str(file.relative_to(stage)):sha(file) for file in files}
records=[json.loads(line) for line in (out/'focused-01.jsonl').read_text().splitlines()]
assert not any(e['Action'] in ['fail','skip'] for e in records)
tests=[(e['Package'],e['Test']) for e in records if e['Action']=='pass' and e.get('Test')]
packages=[e['Package'] for e in records if e['Action']=='pass' and 'Test' not in e]
assert len(packages)==3 and len(tests)>=5
for name in ['TestCanonicalNameExactBytes','TestCanonicalNameConcurrentLifetime','TestCanonicalNameTextBoundary','TestCanonicalNameStorageFactory','TestCanonicalNameStorageParser']:assert any(t[1]==name for t in tests)
report={'scope':'Staged candidate checkpoint, not production promotion/full compiler validation/performance evidence. Exact patch reconstruction readback passed.','sources':source,'patchSha256':sha(out/'candidate.patch'),'focused':{'exitCode':0,'packages':packages,'tests':tests,'records':len(tests),'topLevelTests':sum('/' not in t[1] for t in tests),'stdoutSha256':sha(out/'focused-01.jsonl'),'stderrSha256':sha(out/'focused-01.stderr')},'remaining':['Finish constant and syntax/API boundary propagation and declaration-name flow','Update local generation support','Review final full diff and validate full compiler compatibility before applying','Full conformance/root/CLI/API/emit/services/race/checkptr gates','Frozen matched performance screening and confirmations','Original-native 10x target']}
(out/'checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'files':len(files),'focusedRecords':len(tests),'topLevelTests':report['focused']['topLevelTests'],'packages':len(packages),'reconstruction':'passed'}))
# Delete only this script's verified private reconstruction; retain staged sources.
shutil.rmtree(reconstruction)
