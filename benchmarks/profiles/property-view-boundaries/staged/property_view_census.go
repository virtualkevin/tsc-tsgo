package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"runtime"
	"strconv"
	"strings"
)

func newPropertyViewCensus() *[33]uint64 {
	if os.Getenv("TSC_GO_PROPERTY_VIEW_CENSUS") == "" {
		return nil
	}
	return new([33]uint64)
}

type PropertyViewSnapshot struct {
	CheckerID uint32
	Counts    [33]uint64
	Stacks    map[string][2]uint64
}

func (c *Checker) PropertyViewSnapshot() (PropertyViewSnapshot, bool) {
	if c.propertyViewCensus == nil {
		return PropertyViewSnapshot{}, false
	}
	return PropertyViewSnapshot{c.id, *c.propertyViewCensus, c.propertyViewStacks}, true
}
func WritePropertyViewSnapshots(path string, owners []PropertyViewSnapshot) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	report := struct {
		SchemaVersion int
		Categories    [33]string
		Scope         string
		Owners        []PropertyViewSnapshot
	}{1, [33]string{"lookup", "view-returned", "kept-view-returned", "cache-entry-created", "cache-entry-prepared", "type-query", "type-query-delegated", "type-query-kept", "type-cache-hit", "type-cache-miss", "cache-entry-materialized", "relation-attempt", "relation-early-fallback", "relation-materialized-fallback", "relation-protected-fallback", "relation-accepted", "relation-private-reject", "all-clone-constructors", "write-query", "lookup-nonobject", "lookup-module", "lookup-no-pending", "lookup-materialized-layout", "lookup-resolving", "lookup-bases", "lookup-no-source", "lookup-duplicates", "lookup-missing-or-skipped", "lookup-name-or-kind", "lookup-instantiated-source", "lookup-eligible", "bulk-materializations", "bulk-source-slots"}, "Diagnostic counters on rejected property-view candidate; counts are not CPU costs, safe-reuse proof, or speedups. Entries not materialized at report time may be unreachable or retained; no liveness conclusion.", owners}
	err = json.NewEncoder(f).Encode(report)
	closeErr := f.Close()
	if err != nil {
		return err
	}
	return closeErr
}

func (c *Checker) countPropertyView(index int) {
	if c.propertyViewCensus != nil {
		c.propertyViewCensus[index]++
	}
}

// Ordered classification duplicates only reads, never forces semantic work.
func propertyViewBoundary(t *Type, owner *StructuredType, name string) int {
	if owner == nil {
		return 19
	}
	if t.symbol != nil && t.symbol.Flags&ast.SymbolFlagsValueModule != 0 {
		return 20
	}
	p := owner.pendingMembers
	if p == nil {
		return 21
	}
	if p.memberNames != nil {
		return 22
	}
	if p.resolving {
		return 23
	}
	if p.hasBases || len(p.bases) != 0 {
		return 24
	}
	if p.source == nil {
		return 25
	}
	if len(p.source.entries) != len(p.source.positions) {
		return 26
	}
	i, ok := p.source.positions[name]
	if !ok || p.state(i) == pendingMemberSkipped {
		return 27
	}
	original := p.source.entries[i]
	if original.Name != name || original.Flags&ast.SymbolFlagsProperty == 0 {
		return 28
	}
	if original.CheckFlags&ast.CheckFlagsInstantiated != 0 {
		return 29
	}
	return 30
}
func (c *Checker) observePropertyMaterialization(slots int) {
	if c.propertyViewCensus == nil {
		return
	}
	c.propertyViewCensus[31]++
	c.propertyViewCensus[32] += uint64(slots)
	// Deterministic per-checker systematic sample, not a random estimator.
	if (c.propertyViewCensus[31]-1)&255 != 0 {
		return
	}
	var pcs [12]uintptr
	n := runtime.Callers(2, pcs[:])
	frames := runtime.CallersFrames(pcs[:n])
	var b strings.Builder
	for {
		frame, more := frames.Next()
		b.WriteString(frame.Function)
		b.WriteByte(':')
		b.WriteString(strconv.Itoa(frame.Line))
		b.WriteByte('\n')
		if !more {
			break
		}
	}
	if n == len(pcs) {
		b.WriteString("possibly truncated\n")
	}
	if c.propertyViewStacks == nil {
		c.propertyViewStacks = make(map[string][2]uint64)
	}
	key := b.String()
	v := c.propertyViewStacks[key]
	v[0]++
	v[1] += uint64(slots)
	c.propertyViewStacks[key] = v
}
