package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"sync"
)

// This observer never reuses a semantic result. Keys are retained only for one
// resolveCall lifetime, capped at 4096; the registry retains counters only.
type argumentRequestCounts struct{ Frames, Requests, Repeated, SameResult, DifferentResult, BudgetChanged, Untracked uint64 }
type argumentRequestKey struct {
	Argument                                *ast.Node
	Context                                 *Type
	Mode                                    CheckMode
	Relation                                *Relation
	FlowDepth, ResolutionStart, MapperDepth int
}
type argumentRequestFrame struct {
	counts *argumentRequestCounts
	seen   map[argumentRequestKey]*Type
}

var argumentRequestPath = os.Getenv("TSC_GO_ARGUMENT_REQUEST_CENSUS")
var argumentRequestRegistry struct {
	sync.Mutex
	Owners []*argumentRequestCounts
}

func newArgumentRequestCounts() *argumentRequestCounts {
	if argumentRequestPath == "" {
		return nil
	}
	p := &argumentRequestCounts{}
	argumentRequestRegistry.Lock()
	argumentRequestRegistry.Owners = append(argumentRequestRegistry.Owners, p)
	argumentRequestRegistry.Unlock()
	return p
}
func (p *argumentRequestCounts) frame() *argumentRequestFrame {
	if p == nil {
		return nil
	}
	p.Frames++
	return &argumentRequestFrame{counts: p}
}
func (f *argumentRequestFrame) record(k argumentRequestKey, result *Type, before, after uint32) {
	if f == nil {
		return
	}
	p := f.counts
	p.Requests++
	if before != after {
		p.BudgetChanged++
	}
	if old, ok := f.seen[k]; ok {
		p.Repeated++
		if old == result {
			p.SameResult++
		} else {
			p.DifferentResult++
		}
		return
	}
	if len(f.seen) >= 4096 {
		p.Untracked++
		return
	}
	if f.seen == nil {
		f.seen = make(map[argumentRequestKey]*Type)
	}
	f.seen[k] = result
}
func WriteArgumentRequestCensus() error {
	if argumentRequestPath == "" {
		return nil
	}
	argumentRequestRegistry.Lock()
	defer argumentRequestRegistry.Unlock()
	b, e := json.MarshalIndent(argumentRequestRegistry.Owners, "", "  ")
	if e != nil {
		return e
	}
	return os.WriteFile(argumentRequestPath, append(b, '\n'), 0600)
}
