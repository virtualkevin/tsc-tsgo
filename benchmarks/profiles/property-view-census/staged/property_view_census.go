package checker

import (
	"encoding/json"
	"os"
)

func newPropertyViewCensus() *[19]uint64 {
	if os.Getenv("TSC_GO_PROPERTY_VIEW_CENSUS") == "" {
		return nil
	}
	return new([19]uint64)
}

type PropertyViewSnapshot struct {
	CheckerID uint32
	Counts    [19]uint64
}

func (c *Checker) PropertyViewSnapshot() (PropertyViewSnapshot, bool) {
	if c.propertyViewCensus == nil {
		return PropertyViewSnapshot{}, false
	}
	return PropertyViewSnapshot{c.id, *c.propertyViewCensus}, true
}
func WritePropertyViewSnapshots(path string, owners []PropertyViewSnapshot) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	report := struct {
		SchemaVersion int
		Categories    [19]string
		Scope         string
		Owners        []PropertyViewSnapshot
	}{1, [19]string{"lookup", "view-returned", "kept-view-returned", "cache-entry-created", "cache-entry-prepared", "type-query", "type-query-delegated", "type-query-kept", "type-cache-hit", "type-cache-miss", "cache-entry-materialized", "relation-attempt", "relation-early-fallback", "relation-materialized-fallback", "relation-protected-fallback", "relation-accepted", "relation-private-reject", "all-clone-constructors", "write-query"}, "Diagnostic counters on rejected property-view candidate; counts are not CPU costs, safe-reuse proof, or speedups. Entries not materialized at report time may be unreachable or retained; no liveness conclusion.", owners}
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
