package checker

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"maps"
	"os"
	"path/filepath"
	"runtime/pprof"
	"strings"
	"sync"
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/parser"
)

func TestSemanticCensusInstantiationLimits(t *testing.T) {
	for _, limit := range []string{"depth", "count"} {
		t.Run(limit, func(t *testing.T) {
			censusTestEnvironment(t)
			c := activeMapperTestChecker()
			c.census = newSemanticCensus(1)
			input := c.newTypeParameter(nil)
			target := c.newIntrinsicType(TypeFlagsString, "string")
			c.errorType = c.newIntrinsicType(TypeFlagsAny, "error")
			mapper := newSimpleTypeMapper(input, target)
			c.pushActiveMapper(mapper)
			defer c.popActiveMapper()
			if c.instantiateType(input, mapper) != target {
				t.Fatal("failed to prime mapper cache with census enabled")
			}
			if limit == "depth" {
				c.instantiationDepth = 100
			} else {
				c.instantiationCount = 5_000_000
			}
			file := parser.ParseSourceFile(ast.SourceFileParseOptions{FileName: "/census-limits.ts", Path: "/census-limits.ts"}, "type First = string;\ntype Second = string;\n", core.ScriptKindTS)
			for _, statement := range file.Statements.Nodes {
				c.currentNode = statement.Name()
				if c.instantiateType(input, mapper) != c.errorType {
					t.Fatal("cached type bypassed limit with census enabled")
				}
			}
			diagnostics := c.diagnostics.GetDiagnosticsForFile(file.FileName())
			if len(diagnostics) != 2 || diagnostics[0].Code() != 2589 || diagnostics[1].Code() != 2589 || diagnostics[0].Pos() == diagnostics[1].Pos() {
				t.Fatal("census changed per-use instantiation-limit diagnostics")
			}
			if c.TotalInstantiationCount != 1 || c.census.budgetRejections != 2 || c.census.diagnostics != 2 {
				t.Fatal("budget rejection accounting lost or performed semantic work")
			}
			if len(c.census.ordered) != 1 || c.census.ordered[0].Calls != 1 || c.census.ordered[0].ReturnedNormally != 1 || len(c.census.stack) != 0 {
				t.Fatal("rejected requests were counted as completed instantiation misses")
			}
		})
	}
}

//go:noinline
func semanticCensusRuntimeLabels(t *testing.T) map[string]string {
	t.Helper()
	var output bytes.Buffer
	if err := pprof.Lookup("goroutine").WriteTo(&output, 1); err != nil {
		t.Fatal(err)
	}
	for _, block := range strings.Split(output.String(), "\n\n") {
		if !strings.Contains(block, "semanticCensusRuntimeLabels") {
			continue
		}
		labels := map[string]string{}
		for _, line := range strings.Split(block, "\n") {
			if text, ok := strings.CutPrefix(line, "# labels: "); ok {
				if err := json.Unmarshal([]byte(text), &labels); err != nil {
					t.Fatal(err)
				}
			}
		}
		return labels
	}
	t.Fatal("current goroutine absent from runtime label probe")
	return nil
}

func TestSemanticCensusRuntimeLabels(t *testing.T) {
	censusTestEnvironment(t)
	t.Setenv("TSC_GO_CENSUS_CPU_LABELS", "1")
	done := make(chan struct{})
	go func() {
		defer close(done)
		pprof.SetGoroutineLabels(context.Background())
		defer pprof.SetGoroutineLabels(context.Background())
		c := &Checker{census: newSemanticCensus(77)}
		check := func(record, family string) {
			want := map[string]string{}
			if record != "" {
				want = map[string]string{"census_checker": "77", "census_record": record, "census_family": family}
			}
			if got := semanticCensusRuntimeLabels(t); !maps.Equal(got, want) {
				t.Fatalf("runtime labels: got %v, want %v", got, want)
			}
		}
		check("", "")
		outer := c.beginCensus(censusKey{family: "outer"})
		check("0", "outer")
		inner := c.beginCensus(censusKey{family: "inner"})
		check("1", "inner")
		inner.returnedNormally = true
		inner.finish(c)
		check("0", "outer")
		outer.returnedNormally = true
		outer.finish(c)
		check("", "")
		outer = c.beginCensus(censusKey{family: "outer"})
		check("0", "outer")
		outer.returnedNormally = true
		outer.finish(c)
		check("", "")
		for i := len(c.census.records); i < censusRecordLimit; i++ {
			c.census.records[censusKey{family: "occupied", mode: uint32(i)}] = &c.census.overflow
		}
		overflow := c.beginCensus(censusKey{family: "capped"})
		check("overflow", "unclassified-record-limit-overflow")
		overflow.returnedNormally = true
		overflow.finish(c)
		check("", "")
	}()
	<-done
}

func censusTestEnvironment(t *testing.T) string {
	t.Helper()
	path := filepath.Join(t.TempDir(), "census.jsonl")
	t.Setenv("TSC_GO_CENSUS", path)
	t.Setenv("TSC_GO_CENSUS_CPU_LABELS", "0")
	censusRegistry.Lock()
	saved := censusRegistry.checkers
	censusRegistry.checkers = nil
	censusRegistry.Unlock()
	t.Cleanup(func() { censusRegistry.Lock(); censusRegistry.checkers = saved; censusRegistry.Unlock() })
	return path
}

func TestSemanticCensusNestedAccounting(t *testing.T) {
	censusTestEnvironment(t)
	c := &Checker{TypeCount: 10, TotalInstantiationCount: 20, census: newSemanticCensus(1)}
	outer := c.beginCensus(censusKey{family: "outer"})
	c.TypeCount += 2
	c.TotalInstantiationCount += 3
	inner := c.beginCensus(censusKey{family: "inner"})
	c.TypeCount += 5
	c.TotalInstantiationCount += 7
	inner.returnedNormally = true
	inner.finish(c)
	c.census.diagnostics++
	outer.returnedNormally = true
	outer.finish(c)
	a, b := outer.record, inner.record
	if a.TypesCreated != 7 || a.Instantiations != 10 || b.TypesCreated != 5 || b.Instantiations != 7 {
		t.Fatal("inclusive creation attribution changed", a, b)
	}
	if a.DiagnosticSpans != 1 || b.DiagnosticSpans != 0 {
		t.Fatal("diagnostic attributed outside its active span")
	}
	if a.InclusiveNanoseconds-a.ExclusiveNanoseconds != b.InclusiveNanoseconds {
		t.Fatal("nested elapsed cost counted twice")
	}
	if a.ExclusiveNanoseconds < 0 || b.ExclusiveNanoseconds < 0 || a.Active != 0 || b.Active != 0 || len(c.census.stack) != 0 {
		t.Fatal("span lifetime/accounting invariant failed")
	}
}

func TestSemanticCensusReentrantAndAbortedSpans(t *testing.T) {
	censusTestEnvironment(t)
	c := &Checker{census: newSemanticCensus(1)}
	key := censusKey{family: "same-raw-key"}
	outer := c.beginCensus(key)
	inner := c.beginCensus(key)
	inner.returnedNormally = true
	inner.deferred = true
	inner.finish(c)
	innerElapsed := inner.record.InclusiveNanoseconds
	outer.returnedNormally = true
	outer.errorResult = true
	outer.finish(c)
	r := outer.record
	if r.Calls != 2 || r.ReturnedNormally != 2 || r.DeferredResults != 1 || r.ErrorResults != 1 || r.NestedSameRawKeyEntries != 1 {
		t.Fatal("reentrant state lost", r)
	}
	if r.ExclusiveNanoseconds != r.InclusiveNanoseconds-innerElapsed {
		t.Fatal("same-record recursive cost was double counted")
	}
	func() {
		defer func() {
			if recover() == nil {
				t.Error("expected test panic")
			}
		}()
		span := c.beginCensus(censusKey{family: "aborted"})
		defer span.finish(c)
		panic("intentional diagnostic test")
	}()
	aborted := c.census.ordered[1]
	if aborted.Calls != 1 || aborted.ReturnedNormally != 0 || aborted.Active != 0 || len(c.census.stack) != 0 {
		t.Fatal("panic was recorded as normal completion")
	}
}

func TestSemanticCensusRecordCap(t *testing.T) {
	censusTestEnvironment(t)
	c := &Checker{census: newSemanticCensus(1)}
	sentinel := &censusRecord{}
	for i := 0; i < censusRecordLimit; i++ {
		c.census.records[censusKey{family: "occupied", mode: uint32(i)}] = sentinel
	}
	for _, name := range []string{"overflow-a", "overflow-b"} {
		span := c.beginCensus(censusKey{family: name})
		span.returnedNormally = true
		span.finish(c)
	}
	if len(c.census.records) != censusRecordLimit || len(c.census.ordered) != 0 {
		t.Fatal("record cap exceeded")
	}
	if c.census.overflow.Calls != 2 || c.census.overflow.ReturnedNormally != 2 || c.census.overflow.ID != -1 || c.census.overflow.Active != 0 {
		t.Fatal("overflow work was silently lost")
	}
}

func TestSemanticCensusFlushRejectsActiveAndExistingOutput(t *testing.T) {
	path := censusTestEnvironment(t)
	c := &Checker{census: newSemanticCensus(1)}
	span := c.beginCensus(censusKey{family: "active"})
	if err := FlushSemanticCensus(); err == nil {
		t.Fatal("flushed active checker")
	}
	if _, err := os.Stat(path); !os.IsNotExist(err) {
		t.Fatal("active flush created output", err)
	}
	span.returnedNormally = true
	span.finish(c)
	if err := FlushSemanticCensus(); err != nil {
		t.Fatal(err)
	}
	before, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if err := FlushSemanticCensus(); err == nil {
		t.Fatal("overwrote prior census")
	}
	after, err := os.ReadFile(path)
	if err != nil || string(after) != string(before) {
		t.Fatal("existing census changed", err)
	}
}

func TestSemanticCensusParallelOwners(t *testing.T) {
	path := censusTestEnvironment(t)
	var wg sync.WaitGroup
	for id := uint32(1); id <= 4; id++ {
		wg.Add(1)
		go func(id uint32) {
			defer wg.Done()
			c := &Checker{census: newSemanticCensus(id)}
			for i := 0; i < 20; i++ {
				span := c.beginCensus(censusKey{family: "owned"})
				c.TypeCount++
				span.returnedNormally = true
				span.finish(c)
			}
		}(id)
	}
	wg.Wait()
	if err := FlushSemanticCensus(); err != nil {
		t.Fatal(err)
	}
	f, err := os.Open(path)
	if err != nil {
		t.Fatal(err)
	}
	defer f.Close()
	dec := json.NewDecoder(f)
	var header map[string]any
	if err := dec.Decode(&header); err != nil {
		t.Fatal(err)
	}
	if header["semanticallyEquivalentResultsProven"] != false {
		t.Fatal("collector claimed semantic equivalence")
	}
	seen := map[uint32]bool{}
	for {
		var record struct {
			CheckerID uint32         `json:"checkerId"`
			Records   []censusRecord `json:"records"`
		}
		err := dec.Decode(&record)
		if err == io.EOF {
			break
		}
		if err != nil {
			t.Fatal(err)
		}
		if seen[record.CheckerID] || len(record.Records) != 1 || record.Records[0].Calls != 20 || record.Records[0].TypesCreated != 20 {
			t.Fatal("checker data mixed or missing", record)
		}
		seen[record.CheckerID] = true
	}
	if len(seen) != 4 {
		t.Fatal("missing checker owners", seen)
	}
}
