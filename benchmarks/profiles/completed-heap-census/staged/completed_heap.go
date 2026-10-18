package execute

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"runtime/pprof"
)

// Diagnostic only: keep the existing Program graph rooted through both snapshots.
// Profile bookkeeping itself allocates; differences are not optimization savings.
func writeCompletedHeap(owner any, tracing bool) error {
	directory := os.Getenv("TSC_GO_COMPLETED_HEAP")
	if directory == "" {
		return nil
	}
	if tracing {
		return fmt.Errorf("completed heap census cannot run with tracing")
	}
	return captureCompletedHeap(owner, directory)
}

func captureCompletedHeap(owner any, directory string) error {
	defer runtime.KeepAlive(owner)
	if err := os.Mkdir(directory, 0o755); err != nil {
		return err
	}
	snapshot := func(name string) (runtime.MemStats, error) {
		var stats runtime.MemStats
		runtime.ReadMemStats(&stats)
		f, err := os.OpenFile(filepath.Join(directory, name+".pb.gz"), os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
		if err != nil {
			return stats, err
		}
		err = pprof.Lookup("allocs").WriteTo(f, 0)
		closeErr := f.Close()
		if err != nil {
			return stats, err
		}
		return stats, closeErr
	}
	before, err := snapshot("before")
	if err != nil {
		return err
	}
	runtime.GC()
	runtime.GC()
	after, err := snapshot("after")
	if err != nil {
		return err
	}
	f, err := os.OpenFile(filepath.Join(directory, "stats.json"), os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	err = json.NewEncoder(f).Encode(struct {
		SchemaVersion  int
		MemProfileRate int
		Before         runtime.MemStats
		After          runtime.MemStats
	}{1, runtime.MemProfileRate, before, after})
	closeErr := f.Close()
	if err != nil {
		return err
	}
	return closeErr
}
