"""Measure the real capacities produced by the pinned toolchain for typed arena growth."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

here=Path(__file__).resolve().parent
module=here.parents[2]/"packages/tsc-go"
types=json.loads((Path(sys.argv[1])/"types.json").read_text())
source='''package main
import ("encoding/json"; "os"; "slices"; "unsafe"; "github.com/microsoft/typescript-go/internal/ast")
type Layout struct { Bytes uintptr; Next map[int]int }
func layout[T any]() Layout {
    var zero T
    result := Layout{unsafe.Sizeof(zero),make(map[int]int)}
    for _, first := range []int{0,2,4,8,16,32,64} {
        for capacity:=first; ; {
            if _,exists:=result.Next[capacity];exists {break}
            request:=min(2*max(1,capacity),256)
            next:=cap(slices.Grow([]T(nil),request))
            result.Next[capacity]=next
            capacity=next
        }
    }
    return result
}
func main() { json.NewEncoder(os.Stdout).Encode(map[string]Layout{
'''
source+=''.join(f'"{t}":layout[ast.{t}](),\n' for t in types)+'}) }\n'
with tempfile.TemporaryDirectory(dir=module/"cmd") as tmp:
    path=Path(tmp)/"main.go"
    path.write_text(source)
    data=subprocess.check_output([os.environ.get("GO","go"),"run",str(path)],cwd=module)
(here/"layout.json").write_text(json.dumps(json.loads(data),indent=2,sort_keys=True)+"\n")
