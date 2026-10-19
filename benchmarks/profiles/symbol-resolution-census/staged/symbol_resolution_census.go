package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"time"
)

const symbolCensusOriginLimit = 100000

var symbolCensusKinds = [9]string{"deferred", "instantiated", "mapped", "reverse-mapped", "accessor", "variable-property", "function-class-module", "enum-member", "alias"}

type symbolResolutionCensus struct {
	Hits           [9]uint64
	Misses         [9]uint64
	Origins        map[string]*symbolResolutionRecord
	DroppedOrigins uint64
	active         *symbolResolutionFrame
}
type symbolResolutionRecord struct {
	Kind                                             int
	Calls, Completed, Cached, ErrorResults           uint64
	InclusiveNs, ExclusiveNs                         int64
	InclusiveInstantiations, ExclusiveInstantiations uint64
}
type symbolResolutionFrame struct {
	parent              *symbolResolutionFrame
	record              *symbolResolutionRecord
	start               time.Time
	startInstantiations uint32
	childNs             int64
	childInstantiations uint64
}

func newSymbolResolutionCensus() *symbolResolutionCensus {
	if os.Getenv("TSC_GO_SYMBOL_RESOLUTION_CENSUS") == "" {
		return nil
	}
	return &symbolResolutionCensus{Origins: make(map[string]*symbolResolutionRecord)}
}

type symbolOriginDeclaration struct {
	File           string
	Pos, End, Kind int
}
type symbolOriginDescriptor struct {
	Kind               int
	Name               string
	Flags              ast.SymbolFlags
	CheckFlags         ast.CheckFlags
	Declarations       []symbolOriginDeclaration
	Unresolved         bool
	InstantiationDepth int
	ActiveMappers      int
}

// This describes origin/context shape, never semantic equivalence. It reads
// existing declaration edges, not lazy compiler IDs or any semantic resolver.
func symbolResolutionOrigin(symbol *ast.Symbol, kind, depth, activeMappers int) string {
	d := symbolOriginDescriptor{Kind: kind, Name: symbol.Name, Flags: symbol.Flags, CheckFlags: symbol.CheckFlags, InstantiationDepth: depth, ActiveMappers: activeMappers}
	if len(symbol.Declarations) == 0 {
		d.Unresolved = true
	}
	for _, declaration := range symbol.Declarations {
		if declaration == nil {
			d.Unresolved = true
			continue
		}
		node := declaration
		for steps := 0; node != nil && !ast.IsSourceFile(node) && steps < 4096; steps++ {
			node = node.Parent
		}
		if node == nil || !ast.IsSourceFile(node) {
			d.Unresolved = true
			continue
		}
		d.Declarations = append(d.Declarations, symbolOriginDeclaration{node.AsSourceFile().FileName(), declaration.Pos(), declaration.End(), int(declaration.Kind)})
	}
	encoded, err := json.Marshal(d)
	if err != nil {
		panic(err)
	}
	return string(encoded)
}
func (c *Checker) beginSymbolResolution(symbol *ast.Symbol, kind int) *symbolResolutionFrame {
	observer := c.symbolResolutionCensus
	observer.Misses[kind]++
	key := symbolResolutionOrigin(symbol, kind, int(c.instantiationDepth), len(c.activeMappers))
	record := observer.Origins[key]
	if record == nil {
		if len(observer.Origins) < symbolCensusOriginLimit {
			record = &symbolResolutionRecord{Kind: kind}
			observer.Origins[key] = record
		} else {
			observer.DroppedOrigins++
		}
	}
	frame := &symbolResolutionFrame{parent: observer.active, record: record, start: time.Now(), startInstantiations: c.TotalInstantiationCount}
	observer.active = frame
	return frame
}
func (c *Checker) endSymbolResolution(frame *symbolResolutionFrame, result *Type, cached bool) {
	elapsed := time.Since(frame.start).Nanoseconds()
	operations := uint64(c.TotalInstantiationCount - frame.startInstantiations)
	observer := c.symbolResolutionCensus
	if observer.active != frame || frame.childNs > elapsed || frame.childInstantiations > operations {
		panic("symbol census nesting invariant")
	}
	observer.active = frame.parent
	if frame.parent != nil {
		frame.parent.childNs += elapsed
		frame.parent.childInstantiations += operations
	}
	if record := frame.record; record != nil {
		record.Calls++
		if result != nil {
			record.Completed++
		}
		if cached {
			record.Cached++
		}
		if result != nil && result == c.errorType {
			record.ErrorResults++
		}
		record.InclusiveNs += elapsed
		record.ExclusiveNs += elapsed - frame.childNs
		record.InclusiveInstantiations += operations
		record.ExclusiveInstantiations += operations - frame.childInstantiations
	}
}

type SymbolResolutionSnapshot struct {
	CheckerID      uint32
	Hits, Misses   [9]uint64
	Origins        map[string]*symbolResolutionRecord
	DroppedOrigins uint64
	Active         bool
}

func (c *Checker) SymbolResolutionSnapshot() (SymbolResolutionSnapshot, bool) {
	o := c.symbolResolutionCensus
	if o == nil {
		return SymbolResolutionSnapshot{}, false
	}
	return SymbolResolutionSnapshot{c.id, o.Hits, o.Misses, o.Origins, o.DroppedOrigins, o.active != nil}, true
}
func WriteSymbolResolutionSnapshots(path string, owners []SymbolResolutionSnapshot) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	report := struct {
		SchemaVersion int
		Kinds         [9]string
		Scope         string
		Owners        []SymbolResolutionSnapshot
	}{1, symbolCensusKinds, "Diagnostic resolver origins, not semantic equivalence. Elapsed intervals are instrumented wall time, not CPU or speedup. Nested observed resolver intervals are subtracted for exclusive fields; other nested work remains. Context/effects and unresolved origins require further classification. No cross-checker reuse is proved.", owners}
	err = json.NewEncoder(f).Encode(report)
	closeErr := f.Close()
	if err != nil {
		return err
	}
	return closeErr
}
