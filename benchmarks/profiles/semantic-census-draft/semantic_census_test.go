package checker

import (
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"sync"
	"testing"
)

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
