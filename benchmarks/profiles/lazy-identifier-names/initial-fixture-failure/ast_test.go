package ast

import (
	"sync"
	"sync/atomic"
	"testing"
)

func TestLazyIdentifierNamesSharedClone(t *testing.T) {
	f := &NodeFactory{}
	file := f.NewSourceFile(SourceFileParseOptions{FileName: "test.ts"}, "", f.NewNodeList(nil), f.NewToken(KindEndOfFile)).AsSourceFile()
	var calls atomic.Int32
	names := map[string]string{"reserved": "reserved"}
	file.SetIdentifierNames(func() map[string]string { calls.Add(1); return names })
	clone := file.Clone(f).AsSourceFile()
	if calls.Load() != 0 {
		t.Fatal("clone eagerly loaded names")
	}
	var wg sync.WaitGroup
	for i := 0; i < 32; i++ {
		wg.Go(func() {
			if file.IdentifierNames()["reserved"] != "reserved" || clone.IdentifierNames()["reserved"] != "reserved" {
				t.Error("missing name")
			}
		})
	}
	wg.Wait()
	if calls.Load() != 1 {
		t.Fatalf("loaded %d times", calls.Load())
	}
	if (&SourceFile{}).IdentifierNames() != nil {
		t.Fatal("uninitialized source file should have no names")
	}
}
