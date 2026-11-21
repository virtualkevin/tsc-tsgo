"""Observe address-sampled pointer-link probes, keeping reads race-free."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / 'packages/tsc-go'
mode = sys.argv[2] if len(sys.argv) > 2 else "linear"
if mode not in ("linear","triangular","triangular-clean"):
    raise ValueError(mode)
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
overlay = {}
def read(path):
    return subprocess.check_output(['git','show','e1eeaab:packages/tsc-go/'+path],cwd=root,text=True)
def save(path,src):
    dest = out / Path(path).name
    dest.write_text(src)
    overlay[str(root/path)] = str(dest)
path = 'internal/core/pointerlinkstore.go'
s = read(path).replace('import "unsafe"','import ("unsafe"; "sync/atomic")').replace('count   int','count   int\n rehashing bool')
s = s.replace('index := int(pointerLinkHash(key) & uint64(mask))','hash := pointerLinkHash(key)\n index := int(hash & uint64(mask))')
s = s.replace('for range len(s.entries)', 'for probes := range len(s.entries)')
needle = 'if entry.value == nil || entry.key == key {'
assert s.count(needle) == 1
s = s.replace(needle,needle+'''
            if key != nil && hash >> 57 == 0 {
                category := 0
                if s.rehashing { category = 2 } else if entry.value == nil { category = 1 }
                pointerProbeBins[category][min(probes, 15)].Add(1)
                pointerProbeSteps[category].Add(uint64(probes + 1))
            }''')
s = s.replace('next := PointerLinkStore[K, V]{entries:', 'next := PointerLinkStore[K, V]{rehashing: true, entries:')
s += '''
var pointerProbeBins [3][16]atomic.Uint64
var pointerProbeSteps [3]atomic.Uint64

func PointerProbeCounts() (result [3][17]uint64) {
    for i := range result {
        for j := range pointerProbeBins[i] { result[i][j] = pointerProbeBins[i][j].Load() }
        result[i][16] = pointerProbeSteps[i].Load()
    }
    return result
}
'''
if mode == "triangular-clean":
    s = read(path).replace("for range len(s.entries)", "for probes := range len(s.entries)")
if mode.startswith("triangular"):
    # Triangular offsets enumerate every slot modulo a power of two.
    step = "index = (index + 1) & mask"
    assert s.count(step) == 1
    s = s.replace(step, "index = (index + probes + 1) & mask")
save(path,s)
if mode == "triangular-clean":
    (out/'overlay.json').write_text(json.dumps({'Replace':overlay}))
    sys.exit(0)
path = 'cmd/tsgo/main.go'
s = read(path)
if 'typescript-go/internal/core"' not in s:
    s=s.replace('"context"', '"context"\n "github.com/microsoft/typescript-go/internal/core"')
s=s.replace('"context"', '"context"\n "encoding/json"')
assert s.count('os.Exit(runMain())') == 1
save(path,s.replace('os.Exit(runMain())','status := runMain(); json.NewEncoder(os.Stderr).Encode(core.PointerProbeCounts()); os.Exit(status)'))
(out/'overlay.json').write_text(json.dumps({'Replace':overlay}))
