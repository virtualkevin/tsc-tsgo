package execute

import (
	"compress/gzip"
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"testing"
)

func TestCompletedHeapArtifacts(t *testing.T) {
	dir := filepath.Join(t.TempDir(), "capture")
	owner := make([]byte, 1024*1024)
	owner[0] = 42
	if err := captureCompletedHeap(owner, dir); err != nil {
		t.Fatal(err)
	}
	for _, name := range []string{"before", "after"} {
		f, err := os.Open(filepath.Join(dir, name+".pb.gz"))
		if err != nil {
			t.Fatal(err)
		}
		z, err := gzip.NewReader(f)
		if err != nil {
			t.Fatal(err)
		}
		data, err := io.ReadAll(z)
		if err != nil || len(data) == 0 {
			t.Fatalf("invalid profile: %v", err)
		}
		z.Close()
		f.Close()
	}
	b, err := os.ReadFile(filepath.Join(dir, "stats.json"))
	if err != nil {
		t.Fatal(err)
	}
	var s struct {
		SchemaVersion  int
		MemProfileRate int
		Before, After  runtime.MemStats
	}
	if err := json.Unmarshal(b, &s); err != nil {
		t.Fatal(err)
	}
	if s.SchemaVersion != 1 || s.MemProfileRate != runtime.MemProfileRate || s.After.NumGC < s.Before.NumGC+2 {
		t.Fatalf("invalid snapshot metadata: %+v", s)
	}
	if owner[0] != 42 {
		t.Fatal("owner corrupted")
	}
	if err := captureCompletedHeap(owner, dir); err == nil {
		t.Fatal("overwrote existing capture")
	}
	b2, _ := os.ReadFile(filepath.Join(dir, "stats.json"))
	if string(b) != string(b2) {
		t.Fatal("changed existing evidence")
	}
}

func TestCompletedHeapDisabledAndTracing(t *testing.T) {
	t.Setenv("TSC_GO_COMPLETED_HEAP", "")
	if err := writeCompletedHeap(nil, true); err != nil {
		t.Fatal(err)
	}
	dir := filepath.Join(t.TempDir(), "capture")
	t.Setenv("TSC_GO_COMPLETED_HEAP", dir)
	if err := writeCompletedHeap(nil, true); err == nil {
		t.Fatal("accepted tracing retention")
	}
	if _, err := os.Stat(dir); !os.IsNotExist(err) {
		t.Fatal("created rejected capture")
	}
}
