"""Use the existing name link for a mapped member whose key has identical identity."""
import json
from pathlib import Path
import subprocess
import sys

here=Path(__file__).resolve().parent
root=here.parents[2]/"packages/tsc-go"
out=Path(sys.argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
overlay={}
def edit(file,changes):
    src=subprocess.check_output(["git","show","bd1baea:packages/tsc-go/"+file],cwd=root,text=True)
    for a,b in changes:
        assert src.count(a)==1,a
        src=src.replace(a,b)
    path=out/Path(file).name
    path.write_text(src)
    overlay[str(root/file)]=str(path)

edit("internal/checker/types.go",[
    ("functionOrConstructorChecked bool","functionOrConstructorChecked bool\n    mappedKeyIsName bool")])
edit("internal/checker/checker.go",[
    ("valueLinks.nameType = c.getUnionType([]*Type{valueLinks.nameType, propNameType})\n\t\t\t\tmappedLinks := c.mappedSymbolLinks.Get(existingProp)", """mappedLinks := c.mappedSymbolLinks.Get(existingProp)
                if valueLinks.mappedKeyIsName {
                    mappedLinks.keyType = valueLinks.nameType
                    valueLinks.mappedKeyIsName = false
                }
                valueLinks.nameType = c.getUnionType([]*Type{valueLinks.nameType, propNameType})"""),
    ("mappedLinks := c.mappedSymbolLinks.Get(prop)\n\t\t\t\tmappedLinks.keyType = keyType\n\t\t\t\tif modifiersProp != nil {\n\t\t\t\t\tmappedLinks.syntheticOrigin = modifiersProp", """valueLinks.mappedKeyIsName = keyType == propNameType
                if !valueLinks.mappedKeyIsName || modifiersProp != nil {
                    mappedLinks := c.mappedSymbolLinks.New(prop)
                    mappedLinks.keyType = keyType
                    mappedLinks.syntheticOrigin = modifiersProp
                }
                if modifiersProp != nil {"""),
    ("mapper := appendTypeMapping(mappedType.AsMappedType().mapper, c.getTypeParameterFromMappedType(mappedType), c.mappedSymbolLinks.Get(symbol).keyType)", """parameter := c.getTypeParameterFromMappedType(mappedType)
        keyType := links.nameType
        if !links.mappedKeyIsName { keyType = c.mappedSymbolLinks.Get(symbol).keyType }
        mapper := appendTypeMapping(mappedType.AsMappedType().mapper, parameter, keyType)""")])
if "--count" in sys.argv:
    path=out/"checker.go"
    src=path.read_text()
    for old,new in [
        ("type Checker struct {", """var keyCounts [6]atomic.Uint64
func KeyCounts() [6]uint64 {
    var counts [6]uint64
    for i:=range counts {counts[i]=keyCounts[i].Load()}
    return counts
}
type Checker struct {"""),
        ("valueLinks.mappedKeyIsName = keyType == propNameType", """valueLinks.mappedKeyIsName = keyType == propNameType
            keyCounts[0].Add(1)
            if valueLinks.mappedKeyIsName {keyCounts[1].Add(1); if modifiersProp==nil {keyCounts[2].Add(1)}}"""),
        ("mappedLinks.keyType = valueLinks.nameType", "keyCounts[3].Add(1)\n mappedLinks.keyType = valueLinks.nameType"),
        ("keyType := links.nameType", "if links.mappedKeyIsName {keyCounts[4].Add(1)} else {keyCounts[5].Add(1)}\n keyType := links.nameType"),
    ]:
        assert src.count(old)==1,old
        src=src.replace(old,new)
    path.write_text(src)
    edit("cmd/tsgo/main.go", [('"context"','"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
         ("os.Exit(runMain())","status:=runMain(); json.NewEncoder(os.Stderr).Encode(checker.KeyCounts()); os.Exit(status)")])
(out/"overlay.json").write_text(json.dumps({"Replace":overlay}))
overlay[str(root/"internal/checker/mapped_key_experiment_test.go")] = str(here/"keys_test.go.txt")
(out/"test-overlay.json").write_text(json.dumps({"Replace":overlay}))
