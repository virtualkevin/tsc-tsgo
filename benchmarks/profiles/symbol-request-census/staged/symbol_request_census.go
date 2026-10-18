package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"weak"
)

const symbolRequestLimit = 32768

type symbolRequestKey struct {
	symbol weak.Pointer[ast.Symbol]
	mapper weak.Pointer[TypeMapper]
}
type symbolRequestState struct {
	flags                 ast.SymbolFlags
	checkFlags            ast.CheckFlags
	declarations          int
	parent                weak.Pointer[ast.Symbol]
	valueDeclaration      weak.Pointer[ast.Node]
	resolved, write, name weak.Pointer[Type]
	target                weak.Pointer[ast.Symbol]
	mapper                weak.Pointer[TypeMapper]
}
type SymbolRequestCounts struct {
	Requests                     uint64
	NewKeys                      uint64
	RepeatedSameObservedState    uint64
	RepeatedChangedObservedState uint64
	UntrackedAtCapacity          uint64
}
type symbolRequestCensus struct {
	entries map[symbolRequestKey]symbolRequestState
	limit   int
	// Nil mapper, simple, array, merged, unknown. No semantic queries are issued.
	counts [5]SymbolRequestCounts
}

func newSymbolRequestCensus() *symbolRequestCensus {
	if os.Getenv("TSC_GO_SYMBOL_REQUEST_CENSUS") == "" {
		return nil
	}
	return &symbolRequestCensus{entries: make(map[symbolRequestKey]symbolRequestState), limit: symbolRequestLimit}
}
func (s *symbolRequestCensus) observe(symbol *ast.Symbol, mapper *TypeMapper, links *ValueSymbolLinks) {
	kind := 0
	if mapper != nil {
		switch mapper.Kind() {
		case TypeMapperKindSimple:
			kind = 1
		case TypeMapperKindArray:
			kind = 2
		case TypeMapperKindMerged:
			kind = 3
		default:
			kind = 4
		}
	}
	row := &s.counts[kind]
	row.Requests++
	key := symbolRequestKey{weak.Make(symbol), weak.Make(mapper)}
	old, found := s.entries[key]
	if !found && len(s.entries) >= s.limit {
		row.UntrackedAtCapacity++
		return
	}
	state := symbolRequestState{symbol.Flags, symbol.CheckFlags, len(symbol.Declarations), weak.Make(symbol.Parent), weak.Make(symbol.ValueDeclaration), weak.Make(links.resolvedType), weak.Make(links.writeType), weak.Make(links.nameType), weak.Make(links.target), weak.Make(links.mapper)}
	if !found {
		row.NewKeys++
	} else if old == state {
		row.RepeatedSameObservedState++
	} else {
		row.RepeatedChangedObservedState++
	}
	s.entries[key] = state
}

type SymbolRequestSnapshot struct {
	CheckerID   uint32
	Limit       int
	TrackedKeys int
	Counts      [5]SymbolRequestCounts
}

func (c *Checker) SymbolRequestSnapshot() (SymbolRequestSnapshot, bool) {
	s := c.symbolRequestCensus
	if s == nil {
		return SymbolRequestSnapshot{}, false
	}
	return SymbolRequestSnapshot{c.id, s.limit, len(s.entries), s.counts}, true
}
func WriteSymbolRequestSnapshots(path string, owners []SymbolRequestSnapshot) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	report := struct {
		SchemaVersion int
		MapperKinds   [5]string
		Scope         string
		Owners        []SymbolRequestSnapshot
	}{1, [5]string{"nil", "simple", "array", "merged", "unknown"}, "Bounded first-key ledger of actual newInstantiatedSymbolWithLinks entries. Weak identity keys and selected state only; repeats are not equivalent semantic requests or safe reuse. Changed state compares against the last tracked request. Capacity misses are unknown, not unique. No cost or speedup claim.", owners}
	err = json.NewEncoder(f).Encode(report)
	closeErr := f.Close()
	if err != nil {
		return err
	}
	return closeErr
}
