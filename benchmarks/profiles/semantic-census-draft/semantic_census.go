package checker

// Diagnostic-only draft. This file is not part of the production compiler.
import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"runtime/pprof"
	"strconv"
	"sync"
	"time"

	"github.com/microsoft/typescript-go/internal/ast"
)

const censusRecordLimit = 50_000

type censusKey struct {
	family                                                        string
	node                                                          *ast.Node
	symbol                                                        *ast.Symbol
	typ                                                           *Type
	mapper                                                        *TypeMapper
	alias                                                         *TypeAlias
	mode                                                          uint32
	candidates, resolving                                         bool
	flowDepth, instantiationDepth, activeMappers, resolutionStart int
}

type censusRecord struct {
	ID                                                                                               int
	Family, NodeAddress, SymbolAddress, TypeAddress, MapperAddress, AliasAddress                     string
	File                                                                                             string
	Pos, End                                                                                         int
	Kind                                                                                             uint16
	Mode                                                                                             uint32
	Candidates, Resolving                                                                            bool
	FlowDepth, InstantiationDepth, ActiveMappers, ResolutionStart                                    int
	Calls, ReturnedNormally, ErrorResults, DeferredResults, DiagnosticSpans, NestedSameRawKeyEntries uint64
	InclusiveNanoseconds, ExclusiveNanoseconds                                                       int64
	TypesCreated, Instantiations                                                                     uint64
	Active                                                                                           int `json:"-"`
	labelContext                                                                                     context.Context
}

type semanticCensus struct {
	checkerID        uint32
	records          map[censusKey]*censusRecord
	ordered          []*censusRecord
	overflow         censusRecord
	stack            []*censusSpan
	diagnostics      uint64
	budgetRejections uint64
	cpuLabels        bool
}

type censusSpan struct {
	owner                                   *semanticCensus
	record                                  *censusRecord
	start                                   time.Time
	children                                int64
	diagnostics                             uint64
	types, instantiations                   uint32
	returnedNormally, errorResult, deferred bool
	parentContext                           context.Context
}

var censusRegistry struct {
	sync.Mutex
	checkers []*semanticCensus
}

func newSemanticCensus(id uint32) *semanticCensus {
	if os.Getenv("TSC_GO_CENSUS") == "" {
		return nil
	}
	s := &semanticCensus{checkerID: id, records: make(map[censusKey]*censusRecord), cpuLabels: os.Getenv("TSC_GO_CENSUS_CPU_LABELS") == "1"}
	s.overflow.ID = -1
	s.overflow.Family = "unclassified-record-limit-overflow"
	if s.cpuLabels {
		s.overflow.labelContext = pprof.WithLabels(context.Background(), pprof.Labels("census_checker", strconv.FormatUint(uint64(id), 10), "census_record", "overflow", "census_family", "unclassified-record-limit-overflow"))
	}
	censusRegistry.Lock()
	censusRegistry.checkers = append(censusRegistry.checkers, s)
	censusRegistry.Unlock()
	return s
}

func (c *Checker) beginCensus(key censusKey) *censusSpan {
	s := c.census
	key.flowDepth = len(c.flowLoopStack)
	key.instantiationDepth = int(c.instantiationDepth)
	key.activeMappers = len(c.activeMappers)
	key.resolutionStart = c.resolutionStart
	r := s.records[key]
	if r == nil {
		if len(s.records) >= censusRecordLimit {
			r = &s.overflow
		} else {
			r = &censusRecord{ID: len(s.ordered), Family: key.family, NodeAddress: fmt.Sprintf("%p", key.node), SymbolAddress: fmt.Sprintf("%p", key.symbol), TypeAddress: fmt.Sprintf("%p", key.typ), MapperAddress: fmt.Sprintf("%p", key.mapper), AliasAddress: fmt.Sprintf("%p", key.alias), Mode: key.mode, Candidates: key.candidates, Resolving: key.resolving, FlowDepth: key.flowDepth, InstantiationDepth: key.instantiationDepth, ActiveMappers: key.activeMappers, ResolutionStart: key.resolutionStart}
			if n := key.node; n != nil {
				r.Pos = n.Pos()
				r.End = n.End()
				r.Kind = uint16(n.Kind)
				if f := ast.GetSourceFileOfNode(n); f != nil {
					r.File = f.FileName()
				}
			}
			if s.cpuLabels {
				r.labelContext = pprof.WithLabels(context.Background(), pprof.Labels("census_checker", strconv.FormatUint(uint64(s.checkerID), 10), "census_record", strconv.Itoa(r.ID), "census_family", r.Family))
			}
			s.records[key] = r
			s.ordered = append(s.ordered, r)
		}
	}
	r.Calls++
	if r.Active > 0 {
		r.NestedSameRawKeyEntries++
	}
	r.Active++
	span := &censusSpan{owner: s, record: r, diagnostics: s.diagnostics, types: c.TypeCount, instantiations: c.TotalInstantiationCount, parentContext: context.Background()}
	if len(s.stack) > 0 {
		span.parentContext = s.stack[len(s.stack)-1].record.labelContext
	}
	if s.cpuLabels {
		pprof.SetGoroutineLabels(r.labelContext)
	}
	s.stack = append(s.stack, span)
	span.start = time.Now()
	return span
}

func (span *censusSpan) finish(c *Checker) {
	elapsed := time.Since(span.start).Nanoseconds()
	s, r := span.owner, span.record
	if len(s.stack) == 0 || s.stack[len(s.stack)-1] != span {
		panic("census span stack mismatch")
	}
	s.stack = s.stack[:len(s.stack)-1]
	if len(s.stack) > 0 {
		s.stack[len(s.stack)-1].children += elapsed
	}
	r.Active--
	r.InclusiveNanoseconds += elapsed
	r.ExclusiveNanoseconds += elapsed - span.children
	r.TypesCreated += uint64(c.TypeCount - span.types)
	r.Instantiations += uint64(c.TotalInstantiationCount - span.instantiations)
	if span.returnedNormally {
		r.ReturnedNormally++
	}
	if span.errorResult {
		r.ErrorResults++
	}
	if span.deferred {
		r.DeferredResults++
	}
	if s.diagnostics != span.diagnostics {
		r.DiagnosticSpans++
	}
	if s.cpuLabels {
		pprof.SetGoroutineLabels(span.parentContext)
	}
}

// Uses existing AST/symbol fields only; it must never resolve a type or force a lazy ID.
func censusSymbolOrigin(s *ast.Symbol) *ast.Node {
	if s == nil {
		return nil
	}
	if s.ValueDeclaration != nil {
		return s.ValueDeclaration
	}
	if len(s.Declarations) > 0 {
		return s.Declarations[0]
	}
	return nil
}

// Call only once after an ordinary, non-watch CLI compilation has joined all workers.
// API/LSP/watch mode is intentionally outside this diagnostic draft's lifecycle.
func FlushSemanticCensus() error {
	path := os.Getenv("TSC_GO_CENSUS")
	if path == "" {
		return nil
	}
	censusRegistry.Lock()
	defer censusRegistry.Unlock()
	for _, s := range censusRegistry.checkers {
		if len(s.stack) != 0 {
			return fmt.Errorf("checker %d has active census spans", s.checkerID)
		}
	}
	f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o600)
	if err != nil {
		return err
	}
	encoder := json.NewEncoder(f)
	header := map[string]any{"schemaVersion": 1, "kind": "diagnostic-construction-census", "recordLimitPerChecker": censusRecordLimit, "semanticallyEquivalentResultsProven": false, "limitations": []string{"Origins and raw pointer contexts are not context-complete semantic identities; every record remains unclassified for sharing.", "Pointer identities apply only within this process. File/position/kind is not a cross-process equivalence proof.", "Elapsed time includes scheduling/GC and instrumentation effects; it is not CPU time or a speedup estimate.", "Nested creation and instantiation counters are inclusive; do not sum them as distinct work.", "Optional CPU labels perturb execution and require an uninstrumented control. Labels assume the standalone CLI owns goroutine profiling labels; inherited labels on spawned work prevent an automatic exclusive-CPU interpretation.", "Only selected miss boundaries and the type-instantiation budget guard are instrumented; other computations and limits remain uncovered.", "Overflow combines unrelated requests; its recursion count is not meaningful and its cost is unclassified."}}
	if err = encoder.Encode(header); err != nil {
		f.Close()
		return err
	}
	for _, s := range censusRegistry.checkers {
		value := map[string]any{"checkerId": s.checkerID, "cpuLabels": s.cpuLabels, "diagnosticAdditions": s.diagnostics, "instantiationBudgetRejections": s.budgetRejections, "records": s.ordered, "overflow": s.overflow}
		if err = encoder.Encode(value); err != nil {
			f.Close()
			return err
		}
	}
	return f.Close()
}
