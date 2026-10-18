package compiler

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"sort"
	"sync"
)

// Diagnostic overlay only. Pointer keys distinguish source identity but retain
// source graphs until process exit. Counts cannot establish allocation savings.
type declarationPathObserver struct {
	mu    sync.Mutex
	files map[*ast.SourceFile][2]uint64
}
type declarationPathRow struct{ Explicit, Emitter, Files uint64 }

var declarationPathOutput = os.Getenv("TSC_GO_DECLARATION_PATH_CENSUS")
var declarationPaths declarationPathObserver

func (o *declarationPathObserver) observe(kind int, file *ast.SourceFile) {
	if kind < 0 || kind > 1 || file == nil {
		panic("invalid declaration observation")
	}
	o.mu.Lock()
	defer o.mu.Unlock()
	if o.files == nil {
		o.files = make(map[*ast.SourceFile][2]uint64)
	}
	counts := o.files[file]
	counts[kind]++
	o.files[file] = counts
}
func observeDeclarationPath(kind int, file *ast.SourceFile) {
	if declarationPathOutput != "" {
		declarationPaths.observe(kind, file)
	}
}
func (o *declarationPathObserver) snapshot() []declarationPathRow {
	o.mu.Lock()
	defer o.mu.Unlock()
	histogram := make(map[[2]uint64]uint64)
	for _, counts := range o.files {
		histogram[counts]++
	}
	rows := make([]declarationPathRow, 0, len(histogram))
	for counts, n := range histogram {
		rows = append(rows, declarationPathRow{counts[0], counts[1], n})
	}
	sort.Slice(rows, func(i, j int) bool {
		if rows[i].Explicit != rows[j].Explicit {
			return rows[i].Explicit < rows[j].Explicit
		}
		return rows[i].Emitter < rows[j].Emitter
	})
	return rows
}
func writeDeclarationPaths(path string, o *declarationPathObserver) error {
	data, err := json.MarshalIndent(struct {
		Schema int
		Rows   []declarationPathRow
	}{1, o.snapshot()}, "", "  ")
	if err != nil {
		return err
	}
	f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
	if err != nil {
		return err
	}
	_, err = f.Write(append(data, '\n'))
	closeErr := f.Close()
	if err != nil {
		return err
	}
	return closeErr
}
func WriteDeclarationPathCensus() error {
	if declarationPathOutput == "" {
		return nil
	}
	return writeDeclarationPaths(declarationPathOutput, &declarationPaths)
}
