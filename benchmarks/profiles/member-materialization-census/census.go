package checker

import (
	"encoding/json"
	"os"
	"sync/atomic"
)

// Fixed scalar counters: no semantic pointers, names, or per-instance records.
type materializationCounts struct{ rows [9][3]atomic.Uint64 }

var materializationLabels = [9]string{"start-no-bases", "start-bases", "start-resolving", "retain-count-mismatch", "retain-identity-mismatch", "new-layout", "reused-layout", "table-immediate", "table-later"}

func (c *materializationCounts) record(kind, size, auxiliary int) {
	c.rows[kind][0].Add(1)
	c.rows[kind][1].Add(uint64(size))
	c.rows[kind][2].Add(uint64(auxiliary))
}
func (c *materializationCounts) snapshot() [9][3]uint64 {
	var result [9][3]uint64
	for i := range result {
		for j := range result[i] {
			result[i][j] = c.rows[i][j].Load()
		}
	}
	return result
}

var materializationPath = os.Getenv("TSC_GO_MATERIALIZATION_CENSUS")
var materializations = func() *materializationCounts {
	if materializationPath == "" {
		return nil
	}
	return new(materializationCounts)
}()

func observeMaterialization(kind, size, auxiliary int) {
	if materializations != nil {
		materializations.record(kind, size, auxiliary)
	}
}
func writeMaterializationCounts(path string, c *materializationCounts) error {
	f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
	if err != nil {
		return err
	}
	err = json.NewEncoder(f).Encode(struct {
		Labels  [9]string
		Columns [3]string
		Counts  [9][3]uint64
	}{materializationLabels, [3]string{"events", "entries", "auxiliary"}, c.snapshot()})
	closeErr := f.Close()
	if err != nil {
		return err
	}
	return closeErr
}
func WriteMaterializationCensus() error {
	if materializations == nil {
		return nil
	}
	return writeMaterializationCounts(materializationPath, materializations)
}
