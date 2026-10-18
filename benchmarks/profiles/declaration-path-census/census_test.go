package compiler

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"path/filepath"
	"reflect"
	"sync"
	"testing"
)

func TestDeclarationPathCensusIdentity(t *testing.T) {
	var o declarationPathObserver
	a, b := &ast.SourceFile{}, &ast.SourceFile{}
	o.observe(0, a)
	o.observe(0, a)
	o.observe(1, a)
	o.observe(1, b)
	want := []declarationPathRow{{0, 1, 1}, {2, 1, 1}}
	if !reflect.DeepEqual(o.snapshot(), want) {
		t.Fatal(o.snapshot())
	}
}
func TestDeclarationPathCensusConcurrent(t *testing.T) {
	var o declarationPathObserver
	file := &ast.SourceFile{}
	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func(k int) {
			defer wg.Done()
			for j := 0; j < 100; j++ {
				o.observe(k%2, file)
				o.snapshot()
			}
		}(i)
	}
	wg.Wait()
	if !reflect.DeepEqual(o.snapshot(), []declarationPathRow{{1000, 1000, 1}}) {
		t.Fatal(o.snapshot())
	}
}
func TestDeclarationPathCensusExclusiveOutput(t *testing.T) {
	var o declarationPathObserver
	p := filepath.Join(t.TempDir(), "counts.json")
	if err := writeDeclarationPaths(p, &o); err != nil {
		t.Fatal(err)
	}
	before, _ := os.ReadFile(p)
	var decoded struct {
		Schema int
		Rows   []declarationPathRow
	}
	if err := json.Unmarshal(before, &decoded); err != nil || decoded.Schema != 1 || len(decoded.Rows) != 0 {
		t.Fatal(err, string(before))
	}
	if err := writeDeclarationPaths(p, &o); err == nil {
		t.Fatal("overwrote report")
	}
	after, _ := os.ReadFile(p)
	if string(before) != string(after) {
		t.Fatal("report changed")
	}
}
