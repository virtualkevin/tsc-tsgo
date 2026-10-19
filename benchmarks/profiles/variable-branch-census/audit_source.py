"""Remove exactly the observer additions and require original checker bytes."""
from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parent
original=P.parents[2]/'packages/tsc-go/internal/checker/checker.go'
staged=P/'staged/checker.go'
text=staged.read_text()
def remove_once(fragment,replacement=''):
 global text
 assert text.count(fragment)==1,fragment
 text=text.replace(fragment,replacement,1)
remove_once('\tvariableBranchCensus                        *variableBranchCensus\n')
remove_once('\tc.variableBranchCensus = newVariableBranchCensus()\n')
remove_once('checkMode CheckMode) (observedResult *Type) {','checkMode CheckMode) *Type {')
remove_once('\tvar observedFrame *variableBranchFrame\n\tif c.variableBranchCensus != nil {\n\t\tobservedFrame = c.beginVariableBranch(declaration.Kind, includeOptionality, checkMode)\n\t\tdefer func() { c.endVariableBranch(observedFrame, observedResult) }()\n\t}\n')
branches=re.findall(r'^\t+observedFrame.selectBranch\((\d+)\)\n',text,re.M)
assert sorted(map(int,branches))==list(range(1,19))
text=re.sub(r'^\t+observedFrame.selectBranch\(\d+\)\n','',text,flags=re.M)
assert text.encode()==original.read_bytes()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(P/'source-audit.json').write_text(json.dumps(dict(passed=True,scope='Removing the explicit observer field, initialization, named return, guarded defer, and 18 branch markers restores byte-identical retained checker source. This is not a proof of observer noninterference.',originalSha256=sha(original),stagedSha256=sha(staged),auditorSha256=sha(Path(__file__))),indent=2)+'\n')
print('Observer-stripped checker is byte-identical to retained production.')
